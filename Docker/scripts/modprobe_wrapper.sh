#!/bin/bash
# modprobe wrapper for cEOS running on Docker Desktop (macOS / linuxkit kernel).
#
# cEOS EosStage2 calls modprobe for several kernel modules that are either
# built into the linuxkit kernel or are hardware-specific EOS modules with no
# corresponding .ko file. Stock modprobe fails for both cases, aborting boot.
#
# This wrapper:
#   - Succeeds silently for built-in modules (listed in modules.builtin)
#   - Succeeds silently for any module with no loadable .ko file available
#   - Delegates to the real kmod binary for all other cases

# Extract module name: first non-flag, non-parameter argument
MODULE=""
for arg in "$@"; do
    case "$arg" in
        -*)    continue ;;   # skip flags  (-q, --dry-run, etc.)
        *=*)   continue ;;   # skip params (toggle_BfdShmemStats_enabled=1, etc.)
        *)     MODULE="$arg"; break ;;
    esac
done

[ -z "$MODULE" ] && exec /bin/kmod.real "$@"

KVER=$(uname -r)
BUILTIN="/lib/modules/${KVER}/modules.builtin"
MODDEP="/lib/modules/${KVER}/modules.dep"

# Case 1: module is built into the kernel
if [ -f "$BUILTIN" ] && grep -qE "/${MODULE}[./]" "$BUILTIN" 2>/dev/null; then
    exit 0
fi

# Case 2: no .ko file exists for this module (EOS hardware-specific modules)
if [ -f "$MODDEP" ] && ! grep -qE "/${MODULE}\.ko" "$MODDEP" 2>/dev/null; then
    if ! find "/lib/modules/${KVER}" -name "${MODULE}.ko*" 2>/dev/null | grep -q .; then
        exit 0
    fi
fi

# Default: call the real kmod
exec /bin/kmod.real "$@"
