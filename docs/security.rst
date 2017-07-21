Security
========

zugbruecke is **notoriously insecure by design**.

- **DO NOT** run it on any system directly exposed to the internet! Have a firewall on at all times!
- **DO NOT** run untrusted code (or DLLs)!
- **DO NOT** use zugbruecke for any security related tasks such as encryption, decryption,
  authentication and handling of keys or passwords!
- **DO NOT** run it with root / super users privileges!

The following problems also directly apply to zugbruecke:

- Wine can in fact theoretically run (some) Windows malware: https://en.wikipedia.org/wiki/Wine_(software)#Security
- **NEVER run Wine as root**: https://wiki.winehq.org/FAQ#Should_I_run_Wine_as_root.3F
