.. _security:

.. index::
	triple: root; super user; privileges

Security
========

*zugbruecke* is **notoriously insecure by design**.

- **DO NOT** run it on any system directly exposed to the internet! Have a firewall on at all times!
- **DO NOT** run untrusted code (or DLLs)!
- **DO NOT** use *zugbruecke* for any security related tasks such as encryption, decryption,
  authentication and handling of keys or passwords!
- **DO NOT** run it with root / super users privileges!

The following problems also directly apply to *zugbruecke*:

- *Wine* can in fact theoretically run (some) `Windows malware`_.
- **NEVER run Wine as root!** See `FAQ at WineHQ`_ for details.

.. _Windows malware: https://en.wikipedia.org/wiki/Wine_(software)#Security
.. _FAQ at WineHQ: https://wiki.winehq.org/FAQ#Should_I_run_Wine_as_root.3F

*zugbruecke* does not actively prohibit the its use with root privileges.
