from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        ip_address = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ip_address,
        }
