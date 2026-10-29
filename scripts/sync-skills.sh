#!/usr/bin/env bash
# Shared by sync-rules.yml and the offline regression tests.

load_sync_config() {
    local config_file=$1 violations group folders repos repo skills_path
    declare -gA REPO_FOLDERS=() REPO_SKILLS_PATHS=()

    violations=$(jq -r '
        (.exclusiveFolders // []) as $exclusive
        | [.groups[] as $group | $group.repos[] | {repo: ., folders: $group.folders}]
        | group_by(.repo)
        | map({repo: .[0].repo, folders: (map(.folders[]) | unique)})
        | .[] as $entry
        | $exclusive[] as $set
        | ($entry.folders - ($entry.folders - $set)) as $hit
        | select(($hit | length) > 1)
        | "\($entry.repo): \($hit | join(" + "))"
    ' "$config_file") || return 1
    if [ -n "$violations" ]; then
        echo "❌ Repos recebendo pastas mutuamente exclusivas (exclusiveFolders):"
        echo "$violations"
        return 1
    fi

    # Validate every group before any repository can be copied, even with a repo filter.
    while IFS= read -r group; do
        folders=$(jq -r --arg group "$group" '.groups[$group].folders | join(",")' "$config_file") || return 1
        repos=$(jq -r --arg group "$group" '.groups[$group].repos[]' "$config_file") || return 1
        skills_path=$(jq -r --arg group "$group" '.groups[$group].skillsPath // ".claude/skills"' "$config_file") || return 1
        # Only the two supported roots can be mirrored/pruned.
        case "$skills_path" in
            .claude/skills|.agents/skills) ;;
            *) echo "❌ skillsPath inválido no grupo $group: $skills_path"; return 1 ;;
        esac
        for repo in $repos; do
            if [ -n "${REPO_SKILLS_PATHS[$repo]:-}" ] && [ "${REPO_SKILLS_PATHS[$repo]}" != "$skills_path" ]; then
                echo "❌ Destinos de skills conflitantes para $repo: ${REPO_SKILLS_PATHS[$repo]} e $skills_path (grupo $group)"
                return 1
            fi
            REPO_SKILLS_PATHS[$repo]=$skills_path
            if [ -n "${REPO_FOLDERS[$repo]:-}" ]; then
                REPO_FOLDERS[$repo]="${REPO_FOLDERS[$repo]},$folders"
            else
                REPO_FOLDERS[$repo]=$folders
            fi
        done
    done < <(jq -r '.groups | keys[]' "$config_file")
}

sync_target_branches() {
    printf '%s\n' development staging master mirror
    if [ "$1" = zoppy-os ]; then
        printf '%s\n' zoppy-os-v2
    fi
}

# Runs in the destination checkout. Invoke as a separate process so -e applies
# to copy/prune failures even when the workflow checks the exit status with `if`.
sync_repo_skills() {
    local workspace=$1 skills_path=$2
    shift 2
    local folder source skill_dir skill_name existing name
    local -A canon_skills=()

    case "$skills_path" in
        .claude/skills|.agents/skills) ;;
        *) echo "❌ skillsPath inválido: $skills_path"; return 1 ;;
    esac

    if [ "$skills_path" = .agents/skills ]; then
        if [ -L .claude/skills ]; then
            if [ "$(readlink .claude/skills)" != ../.agents/skills ]; then
                echo "❌ .claude/skills aponta para outro destino; ajuste o link para ../.agents/skills. Nada foi copiado."
                return 1
            fi
        elif [ -e .claude/skills ]; then
            echo "❌ .claude/skills existe e não é link simbólico (diretório real ou arquivo). Migre seu conteúdo para .agents/skills antes do sync. Nada foi apagado ou copiado."
            return 1
        fi
    fi

    # Refuse symlinked canonical destinations before pruning or copying.
    if [ -L "$skills_path" ]; then
        echo "❌ O destino $skills_path deve ser um diretório real."
        return 1
    fi
    for folder in "$@"; do
        source="$workspace/skills/$folder"
        [ -d "$source" ] || continue
        for skill_dir in "$source"/*/; do
            [ -d "$skill_dir" ] || continue
            skill_name=$(basename "$skill_dir")
            if [ -L "$skills_path/$skill_name" ]; then
                echo "❌ A skill $skills_path/$skill_name é um link simbólico; sync cancelado."
                return 1
            fi
            canon_skills[$skill_name]=1
        done
    done

    mkdir -p "$skills_path"
    if [ "$skills_path" = .agents/skills ]; then
        mkdir -p .claude
        if [ ! -L .claude/skills ]; then
            ln -s ../.agents/skills .claude/skills
        fi
    fi

    # Prune orphan folders only; root files and unrelated repo paths stay intact.
    for existing in "$skills_path"/*; do
        [ -d "$existing" ] || continue
        name=$(basename "$existing")
        if [ -z "${canon_skills[$name]:-}" ]; then
            rm -r -- "$existing"
            echo "  🗑️  pruned orphan skill: $name"
        fi
    done

    for folder in "$@"; do
        source="$workspace/skills/$folder"
        [ -d "$source" ] || continue
        for skill_dir in "$source"/*/; do
            [ -d "$skill_dir" ] || continue
            skill_name=$(basename "$skill_dir")
            mkdir -p "$skills_path/$skill_name"
            # Trailing slashes mirror contents (including dotfiles). --delete is
            # deliberately scoped to this canonical skill, never the whole root.
            rsync -a --delete -- "$skill_dir" "$skills_path/$skill_name/"
        done
    done

    {
        echo "# Skills synced from Zoppy-crm/.github"
        echo "# Groups: $*"
        for folder in "$@"; do
            source="$workspace/skills/$folder"
            [ -d "$source" ] || continue
            for skill_dir in "$source"/*/; do
                [ -d "$skill_dir" ] || continue
                basename "$skill_dir"
            done
        done
    } > "$skills_path/.synced-from-org"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    set -euo pipefail
    sync_repo_skills "$@"
fi
