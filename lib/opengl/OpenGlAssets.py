

class OpenGlAssets:

    _global_assets = dict()

    @classmethod
    def register(cls, name, asset):
        if name in cls._global_assets:
            raise ValueError("OpenGlAssets: duplicate call to register with name '%s'" % name)
        cls._global_assets[name] = [asset, 1]

    @classmethod
    def unregister(cls, name_or_obj):
        if isinstance(name_or_obj, str):
            if name_or_obj not in cls._global_assets:
                return
            asset = cls._global_assets[name_or_obj]
        else:
            asset = None
            for a in cls._global_assets.values():
                if a[0] == name_or_obj:
                    asset = a[0]
                    break
            if asset is None:
                return
        if asset[1] > 0:
            asset[1] -= 1
        else:
            raise ValueError("Too many calls to OpenGlAssets.unregister('%s')" % name)

    @classmethod
    def has(cls, name):
        return name in cls._global_assets

    @classmethod
    def get(cls, name):
        a = cls._global_assets.get(name)
        a[1] += 1
        return a[0]

    @classmethod
    def usage_count(cls, name):
        return cls._global_assets.get(name, (0,0))[1]

    @classmethod
    def garbage_collect(cls):
        remove = set()
        for name in cls._global_assets:
            asset = cls._global_assets[name]
            if asset[1] < 1:
                remove.add(name)
                if asset[0].is_created():
                    asset[0].release()
        for name in remove:
            del cls._global_assets[name]

    @classmethod
    def dump(cls):
        fmts = "%30s | %8s | %s"
        print(fmts % ("name", "users", "object"))
        for name in cls._global_assets:
            a = cls._global_assets[name]
            print(fmts % (name, a[1], a[0]))
