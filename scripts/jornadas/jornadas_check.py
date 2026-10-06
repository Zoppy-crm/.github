import json
import os
import re
import subprocess
import sys
import urllib.request

import yaml

MARCADOR = '<!-- jornadas-check -->'


def carregar_mapa(caminho):
    doc = yaml.safe_load(open(caminho, encoding='utf-8'))
    extensoes = tuple('.' + e for e in doc['arquivos']['extensoes'])
    excluir = [re.compile(r) for r in doc['arquivos']['excluir']]
    prefixos = []
    for jornada, caminhos in doc['jornadas'].items():
        for c in caminhos:
            prefixos.append((c.rstrip('/'), jornada))
    prefixos.sort(key=lambda p: len(p[0]), reverse=True)
    return extensoes, excluir, prefixos


def elegivel(arquivo, extensoes, excluir):
    if not arquivo.startswith('src/') or not arquivo.endswith(extensoes):
        return False
    relativo = arquivo[len('src/'):]
    return not any(r.search(relativo) for r in excluir)


def jornada_de(arquivo, prefixos):
    for prefixo, jornada in prefixos:
        if arquivo == prefixo or arquivo.startswith(prefixo + '/'):
            return jornada
    return None


def arquivos_novos(base, cabeca):
    saida = subprocess.run(
        ['git', 'diff', '--name-only', '--diff-filter=AR', f'{base}...{cabeca}', '--', 'src'],
        capture_output=True, text=True, check=True
    ).stdout
    return [l.strip() for l in saida.splitlines() if l.strip()]


def sem_jornada(base, cabeca, mapa):
    extensoes, excluir, prefixos = carregar_mapa(mapa)
    orfaos = {}
    for arquivo in arquivos_novos(base, cabeca):
        if elegivel(arquivo, extensoes, excluir) and jornada_de(arquivo, prefixos) is None:
            pasta = arquivo.rsplit('/', 1)[0]
            orfaos.setdefault(pasta, []).append(arquivo)
    return orfaos


def corpo(orfaos):
    if not orfaos:
        return f'{MARCADOR}\n**Jornadas:** todos os arquivos novos deste PR já têm jornada no `jornadas.yml`.'
    linhas = [
        MARCADOR,
        '**Jornadas: arquivos novos sem jornada no `jornadas.yml`**',
        '',
        'A cobertura por jornada vai contá-los como "Nao classificado" até o mapa ser atualizado. '
        'Adicione a pasta (ou o arquivo) na jornada certa do `jornadas.yml`, neste mesmo PR. Isso não bloqueia o merge.',
        ''
    ]
    for pasta in sorted(orfaos):
        arquivos = sorted(orfaos[pasta])
        linhas.append(f'- `{pasta}/`')
        for arquivo in arquivos[:15]:
            linhas.append(f'  - `{arquivo.rsplit("/", 1)[1]}`')
        if len(arquivos) > 15:
            linhas.append(f'  - … e mais {len(arquivos) - 15}')
    return '\n'.join(linhas)


def github(metodo, url, token, dados=None):
    requisicao = urllib.request.Request(
        url, method=metodo,
        data=json.dumps(dados).encode() if dados is not None else None,
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
    )
    with urllib.request.urlopen(requisicao) as resposta:
        return json.loads(resposta.read() or b'null')


def comentar(texto, orfaos):
    token = os.environ['GITHUB_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']
    numero = os.environ['PR_NUMBER']
    api = f'https://api.github.com/repos/{repo}/issues'
    existentes = github('GET', f'{api}/{numero}/comments?per_page=100', token)
    anterior = next((c for c in existentes if MARCADOR in (c.get('body') or '')), None)
    if anterior:
        github('PATCH', f'{api}/comments/{anterior["id"]}', token, {'body': texto})
    elif orfaos:
        github('POST', f'{api}/{numero}/comments', token, {'body': texto})


def main():
    base, cabeca = sys.argv[1], sys.argv[2]
    mapa = sys.argv[3] if len(sys.argv) > 3 else 'jornadas.yml'
    orfaos = sem_jornada(base, cabeca, mapa)
    texto = corpo(orfaos)
    print(texto)
    if os.environ.get('PR_NUMBER'):
        comentar(texto, orfaos)


if __name__ == '__main__':
    main()
