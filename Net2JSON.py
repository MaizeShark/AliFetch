import json


def Netscape2json(netscape_file):
    cookies = []

    with open(netscape_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            fields = line.split("\t")
            if len(fields) != 7:
                continue

            domain, _include_subdomains, path, secure, expires, name, value = fields

            cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "secure": secure.upper() == "TRUE",
            }

            expires = float(expires)
            if expires > 0:
                cookie["expires"] = expires

            cookies.append(cookie)

    return cookies


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python Net2JSON.py <input netscape file> <output json file>")
        sys.exit(1)

    cookies = Netscape2json(sys.argv[1])

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
