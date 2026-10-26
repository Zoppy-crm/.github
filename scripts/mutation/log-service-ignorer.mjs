const MEMBER_TYPES = new Set(['MemberExpression', 'OptionalMemberExpression']);
const CALL_TYPES = new Set(['CallExpression', 'OptionalCallExpression']);

function isLogServiceTarget(node) {
    if (!node) {
        return false;
    }
    if (node.type === 'Identifier') {
        return node.name === 'LogService';
    }
    if (MEMBER_TYPES.has(node.type) && !node.computed && node.property.type === 'Identifier') {
        return node.property.name === 'logService';
    }
    return false;
}

const logServiceIgnorer = {
    shouldIgnore(path) {
        const node = path.node;
        if (!CALL_TYPES.has(node.type)) {
            return undefined;
        }
        const callee = node.callee;
        if (MEMBER_TYPES.has(callee.type) && isLogServiceTarget(callee.object)) {
            return 'Chamada ao LogService';
        }
        return undefined;
    }
};

export const strykerPlugins = [{ kind: 'Ignore', name: 'log-service', value: logServiceIgnorer }];
