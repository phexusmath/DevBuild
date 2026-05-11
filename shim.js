(function() {
    const win = window;
    const prefix = (document.title || "game").replace(/\s+/g, '_') + "_";

    const props = {
        top: { get: () => win },
        parent: { get: () => win },
        self: { get: () => win },
        frameElement: { get: () => null }
    };

    for (let prop in props) {
        try {
            Object.defineProperty(win, prop, { ...props[prop], configurable: true });
        } catch (e) {}
    }

    const storageProxy = {
        getItem: (key) => win.parent.localStorage.getItem(prefix + key),
        setItem: (key, value) => win.parent.localStorage.setItem(prefix + key, value),
        removeItem: (key) => win.parent.localStorage.removeItem(prefix + key),
        key: (index) => {
            const keys = Object.keys(win.parent.localStorage).filter(k => k.startsWith(prefix));
            return keys[index] ? keys[index].replace(prefix, '') : null;
        },
        clear: () => {
            Object.keys(win.parent.localStorage).forEach(k => {
                if (k.startsWith(prefix)) win.parent.localStorage.removeItem(k);
            });
        },
        get length() {
            return Object.keys(win.parent.localStorage).filter(k => k.startsWith(prefix)).length;
        }
    };

    try {
        Object.defineProperty(win, 'localStorage', {
            get: () => storageProxy,
            configurable: true
        });
    } catch (e) {}
})();
