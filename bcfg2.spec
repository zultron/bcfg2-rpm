%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif
%{!?py_ver: %define py_ver %(%{__python} -c 'import sys;print(sys.version[0:3])')}
%global pythonversion %{py_ver}
#%global _rc 1
%global _pre 1

Name:             bcfg2
Version:          1.2.0
#Release:          1%{?_rc:.rc%{_rc}}%{?dist}
Release:          1%{?_pre:.pre%{_pre}}%{?dist}
Summary:          Configuration management system

Group:            Applications/System
License:          BSD
URL:              http://trac.mcs.anl.gov/projects/bcfg2
#Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz
#Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz.gpg
Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_pre:pre%{_pre}}.tar.gz
Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_pre:pre%{_pre}}.tar.gz.gpg
Patch0:           bcfg2-py27-auth.patch
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

%if 0%{?fedora} >= 8
BuildRequires:    python-setuptools-devel
%else
BuildRequires:    python-setuptools
%endif

Requires:         python-lxml
%if 0%{?epel} > 0
Requires:	      python-ssl
%endif

Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(postun): /sbin/service

%description
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

%package server
Summary:          Configuration management server
Group:            System Environment/Daemons
Requires:         bcfg2 = %{version}-%{release}
Requires:         /usr/sbin/sendmail
Requires:         /usr/bin/openssl
Requires:         gamin-python
Requires:         redhat-lsb
Requires:         python-genshi
Requires:         python-cheetah
Requires:         graphviz
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(postun): /sbin/service

%description server
Configuration management server

%package doc
Summary:          Documentation for Bcfg2
Group:            System

BuildRequires:    python-sphinx
BuildRequires:    python-docutils

%description doc
Documentation for Bcfg2.

%prep
#%setup -q -n %{name}-%{version}%{?_rc:rc%{_rc}}
%setup -q -n %{name}-%{version}%{?_pre:pre%{_pre}}
%patch0 -p1 -b .bcfg2-py27-auth

# fixup some paths
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' debian/bcfg2.init
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' debian/bcfg2-server.init
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' tools/bcfg2-cron

%{__perl} -pi -e 's@/usr/lib/bcfg2@%{_libexecdir}@g' debian/bcfg2.cron.daily
%{__perl} -pi -e 's@/usr/lib/bcfg2@%{_libexecdir}@g' debian/bcfg2.cron.hourly

# don't start servers by default
%{__perl} -pi -e 's@chkconfig: (\d+)@chkconfig: -@' debian/bcfg2.init
%{__perl} -pi -e 's@chkconfig: (\d+)@chkconfig: -@' debian/bcfg2-server.init

# get rid of extraneous shebangs
for f in `find src/lib -name \*.py`
do
        %{__sed} -i -e '/^#!/,1d' $f
done

%build
%{__python} -c 'import setuptools; execfile("setup.py")' build
#%{__python} -c 'import setuptools; execfile("setup.py")' build_dtddoc
%{__python} -c 'import setuptools; execfile("setup.py")' build_sphinx


#%{?pythonpath: export PYTHONPATH="%{pythonpath}"}
#%{__python}%{pythonversion} setup.py build_dtddoc
#%{__python}%{pythonversion} setup.py build_sphinx


%install
rm -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/cron.daily
mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_var}/lib/bcfg2
mkdir -p %{buildroot}%{_var}/cache/bcfg2
mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}

mv %{buildroot}%{_bindir}/bcfg2* %{buildroot}%{_sbindir}

install -m 755 debian/bcfg2.init %{buildroot}%{_initrddir}/bcfg2
install -m 755 debian/bcfg2-server.init %{buildroot}%{_initrddir}/bcfg2-server
install -m 755 debian/bcfg2.cron.daily %{buildroot}%{_sysconfdir}/cron.daily/bcfg2
install -m 755 debian/bcfg2.cron.hourly %{buildroot}%{_sysconfdir}/cron.hourly/bcfg2
install -m 755 tools/bcfg2-cron %{buildroot}%{_libexecdir}/bcfg2-cron

install -m 644 debian/bcfg2.default %{buildroot}%{_sysconfdir}/sysconfig/bcfg2
install -m 644 debian/bcfg2-server.default %{buildroot}%{_sysconfdir}/sysconfig/bcfg2-server

touch %{buildroot}%{_sysconfdir}/bcfg2.cert
touch %{buildroot}%{_sysconfdir}/bcfg2.conf
touch %{buildroot}%{_sysconfdir}/bcfg2.key

mv build/sphinx/html/* %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}
#mv build/dtd %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}/

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add bcfg2

%preun
if [ $1 = 0 ]; then
        /sbin/service bcfg2 stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del bcfg2
fi

%postun
if [ "$1" -ge "1" ]; then
        /sbin/service bcfg2 condrestart >/dev/null 2>&1 || :
fi

%post server
/sbin/chkconfig --add bcfg2-server

%preun server
if [ $1 = 0 ]; then
        /sbin/service bcfg2-server stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del bcfg2-server
fi

%postun server
if [ "$1" -ge "1" ]; then
        /sbin/service bcfg2-server condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS examples COPYRIGHT README

%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.cert
%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.conf

%config(noreplace) %{_sysconfdir}/sysconfig/bcfg2
%{_sysconfdir}/cron.daily/bcfg2
%{_sysconfdir}/cron.hourly/bcfg2

%{_initrddir}/bcfg2

%{python_sitelib}/Bcfg2*.egg-info
%dir %{python_sitelib}/Bcfg2
%{python_sitelib}/Bcfg2/__init__.*
%{python_sitelib}/Bcfg2/Client
%{python_sitelib}/Bcfg2/Component.*
%{python_sitelib}/Bcfg2/Logger.*
%{python_sitelib}/Bcfg2/Options.*
%{python_sitelib}/Bcfg2/Proxy.*
%{python_sitelib}/Bcfg2/SSLServer.*
%{python_sitelib}/Bcfg2/Statistics.*

%{_sbindir}/bcfg2
%{_mandir}/man1/bcfg2.1*
%{_mandir}/man5/bcfg2.conf.5*

%{_libexecdir}/bcfg2-cron

%dir %{_var}/cache/bcfg2

%files server
%defattr(-,root,root,-)

%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.key

%config(noreplace) %{_sysconfdir}/sysconfig/bcfg2-server

%{_initrddir}/bcfg2-server

%{python_sitelib}/Bcfg2/Server

%{_datadir}/bcfg2

%{_sbindir}/bcfg2-admin
%{_sbindir}/bcfg2-build-reports
%{_sbindir}/bcfg2-info
%{_sbindir}/bcfg2-ping-sweep
%{_sbindir}/bcfg2-repo-validate
%{_sbindir}/bcfg2-reports
%{_sbindir}/bcfg2-server

%{_mandir}/man8/bcfg2-admin.8*
%{_mandir}/man8/bcfg2-build-reports.8*
%{_mandir}/man8/bcfg2-info.8*
%{_mandir}/man8/bcfg2-repo-validate.8*
%{_mandir}/man8/bcfg2-reports.8*
%{_mandir}/man8/bcfg2-server.8*

%dir %{_var}/lib/bcfg2

%files doc
%defattr(-,root,root,-)
%doc %{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}

%changelog
* Sun Mar 20 2011 Fabian Affolter <fabian@bernewireless.net> - 1.2.0-1.1.pre1
- Added doc subpackage
- Updated to new upstream version 1.2.0pre1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Nov 18 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.1-2
- Added new man page
- Updated doc section (ChangeLog is gone)

* Thu Nov 18 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.1-1
- Updated to new upstream version 1.1.1

* Fri Nov  5 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-3
- Add patch from Gordon Messmer to fix authentication on F14+ (Python 2.7)

* Mon Sep 27 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-2
- Update to final version

* Wed Sep 15 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-1.3.rc5
- Update to 1.1.0rc5:
-
- Packages:
-  - Assign the deps variable before resolution.
-  - Allow xinclude and add XML error handling
-  - Remove log line from black/whitelist test
-  - Allow for whitelisting
-   Patch from IRConan to allow for whitelisted packages in
-   sources.
-  - Treat blacklisted packages as if they don't exist
-   Currently a blacklisted package stops further source processing.
-   This prevents any other sources from defining a good package.
-  - Document new knobs and added schema validator
-  - Move knobs to config.xml
-  - Resolver/Metadata options
-   Patch from Jack Neely to add enable/disable options to the resolver
-   and metadata pareser.
-  - Allow soft relaods and use a checksum for cache file.
-   Use checksum for cache file.
-   Allow reloads of config.xml and sources without downloading everything.
-   Merged config.xml and source processing into a single function.
-  - Expose repo data as a Connector
-  - fix type conflict
-  - invalidate virt_pkgs cache when source data is reloaded
-  - dep resolver rewrite
-   Fix dep resolver to take all providers of a dependency into consideration.
-   Rewrite resolver to be simpler at the same time.
-  - Added support for "apt" and "yum" as non-distro specific magic groups
-
- YUMng:
-  - Better error handling for installs
-  - Deal with any possible Yum verify exceptions
-  - patch from Tim Laszlo to handle verifying broken symlinks
-  - fix bug #931
-   getinstalledgpg() is an RPMng method and is no longer needed in YUMng.
-  - Fix Path type='ignore' traceback (Reported by Thomas Ackermann)
-  - speed improvements, multilib verify bug fixes, configuration knobs
-   The pkg_checks, pkg_verify, installed_action, version_fail_action, and
-   verify_fail_action configuration knobs are all wired back up.  Caching
-   implemented to help speed up the package verify routine.
-   Work arounds for Yum bug: http://yum.baseurl.org/ticket/573
-  - Speed improvements, Enable reinstalls
-   We no longer use RPMng in YUMng.  This improves speed by not calling
-   prelink as yum takes care of that for us.
-   Yum can do reinstalls on package verify fail so lets wire that up.
-  - All gpg-pubkey must be in the proper work queue to be installed.
-   gpg-pubkeys are not packages, yet we treat them as so.  They require
-   special handling for all install/upgrades/etc.  This corrects a
-   condition where gpg-pubkeys were "upgraded" rather than "installed."
-  - YUMng display classes, always compare string versions of packages.
-   The package object here can be either a yum PO or a string.  Comparing
-   strings to POs tracebacks.
-   Display classes for the YUMng driver
-  - YUMng re-implementation of VerifyPackage using the Yum API.
-
- doc:
-  - Some clarifications on Decisions plugin.
-  - Minor fixes to SSHbase documentation
-  - Style fixes
-  - Fix hyperlinks
-  - Add the rest of the altsrc documentation for Ticket #923
-
- schema:
-  - Schema updates for Path type="ignore"
-  - repo-validate: Validate two levels of Group nesting (Fixes
-   Ticket #805)
-
- Misc:
-  - bcfg2-repo-validate: Patch from Joe Digilio to fix tb in Ticket #939
-  - Metadata: Add error message when file monitor fails
-  - bcfg2.spec.in: Fix lxml requirement for bcfg2 client (Reported by tac on IRC)
-  - Tools/__init__.py: Autoload client tools present in the Tools directory
-  - bcfg2-info: Add IPython support (Patch from Jeff Strunk) for Ticket #921
-  - BB: Deprecate BB plugin (Resolves Ticket #923)
-  - bcfg2: Add back the new SSL key options (Fixes Ticket #916)
-   The man page no longer contains the -K option mentioned in Ticket #908.
-   This has been removed since [6013]. We still need the key option available
-   in the client to prevent Ticket #916.
-  - Added prefix option to [server] section
-  - fixes for #910
-  - '-K' is replaced by '--ssl-key'
-  - SSLServer: handle socket errors on shutdown gracefully (Resolves #907 and #909)
-  - bcfg2: fix option parsing for ssl key (Resolves Ticket #908)
-  - Init: Fix traceback from ticket #906
-  - Harmonised log messages
-  - debian: Merge in changes from Arto Jantunen
-  - bcfg2.init: Remove agent mode (no longer exists)
-  - POSIX.py: Fix hardcoded errno value
-  - Don't assume python2.5 is being used on successful hashlib import
-  - Probes: Fix name collapse in case of group specific probes (arch.G20_foo -> arch) (Resolves Ticket #904)
-  - TGenshi/TCheetah: Add base64 encoding support for files handled by non-Cfg plugins
-  - bcfg2-server: logger.error doesn't work when bcfg2.conf doesn't exist
-  - IPS fixups (from RickB)
-  - DBStats: Fix random mysql errors
-  - SSLServer: Retry failed writes
-  - Commit whitelist/blacksupport for glob style entries
-  - Cfg: Allow pull operations to update info.xml files

* Tue Aug 31 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-1.2.rc4
- Add new YUMng driver

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.1.0-1.1.rc4.1
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 20 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.0-1.1.rc4
- Added patch to fix indention

* Tue Jul 20 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.0-0.1.rc4
- Updated to new upstream release candidate RC4

* Sat Jun 19 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.0-0.1.rc3
- Updated to new upstream release candidate RC3 

* Sun May 02 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.0-0.2.rc1
- Changed define to global
- Added graphviz for the server package

* Wed Apr 28 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-0.1.rc1
- Update to 1.1.0rc1
- 
- * Deprecate old-style server POSIX types
- 
-  You will now need to specify Path entries in the bcfg2 server
-  configuration instead of the old ConfigFile, Directory, SymLink
-  entries. A tool for helping you transition existing configurations
-  can be found at:
- 
-      https://trac.mcs.anl.gov/projects/bcfg2/browser/tags/bcfg2_1_1_0rc1/tools/posixunified.py
- 
-  Compatibility with older clients is maintained through the use of
-  the new POSIXCompat plugin which transforms the new Path entries to
-  their older equivalents.
- 
- * New Sphinx documentation
- 
-  We have migrated user documentation to Sphinx. Information about
-  building the documentation from the Bcfg2 source can be found at:
- 
-      https://trac.mcs.anl.gov/projects/bcfg2/wiki/Manual
- 
- * Migrate git plugin to Dulwich
- * New detailed client view and other improvements in Django reports
- * Encap removed
- * New OS X packaging
- * New Upstart client tool
- * Migrate Hostbase to Django 1.1

* Tue Apr 13 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.1-1
- Update to final version

* Fri Nov  6 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.0-2
- Fixup the bcfg2-server init script

* Fri Nov  6 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.0-1
- Update to 1.0.0 final

* Wed Nov  4 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.0-0.5.rc2
- Only require python-ssl on EPEL

* Sat Oct 31 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.0-0.4.rc2
- Update to 1.0.0rc2

* Mon Oct 26 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0.0-0.3.rc1
- Update to 1.0rc1

* Fri Oct 16 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0-0.2.pre5
- Add python-ssl requirement

* Tue Aug 11 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.0-0.1.pre5
- Update to 1.0pre5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.9.6-2
- Rebuild for Python 2.6

* Tue Nov 18 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.6-1
- Update to 0.9.6 final.

* Tue Oct 14 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.6-0.8.pre3
- Update to 0.9.6pre3

* Sat Aug  9 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.6-0.2.pre2
- Update to 0.9.6pre2

* Wed May 28 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.6-0.1.pre1
- Update to 0.9.6pre1

* Fri Feb 15 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.7-1
- Update to 0.9.5.7.

* Fri Feb 15 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.7-1
- Update to 0.9.5.7.

* Fri Jan 11 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.5-1
- Update to 0.9.5.5
- More egg-info entries.

* Wed Jan  9 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.4-1
- Update to 0.9.5.4.

* Tue Jan  8 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.3-1
- Update to 0.9.5.3
- Package egg-info files.

* Mon Nov 12 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5.2-1
- Update to 0.9.5.2

* Mon Nov 12 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5-2
- Fix oops.

* Mon Nov 12 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5-1
- Update to 0.9.5 final.

* Mon Nov 05 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5-0.5.pre7
- Commit new patches to CVS.

* Mon Nov 05 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.5-0.4.pre7
- Update to 0.9.5pre7

* Wed Jun 27 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-4
- Oops, apply right patch

* Wed Jun 27 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-3
- Add patch to fix YUMng problem

* Mon Jun 25 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-2
- Bump revision and rebuild

* Mon Jun 25 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-1
- Update to 0.9.4 final

* Thu Jun 21 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-0.1.pre4
- Update to 0.9.4pre4

* Thu Jun 14 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-0.1.pre3
- Update to 0.9.4pre3

* Tue Jun 12 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.4-0.1.pre2
- Update to 0.9.4pre2

* Tue May 22 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.3-2
- Drop requires on pyOpenSSL
- Add requires on redhat-lsb
- (Fixes #240871)

* Mon Apr 30 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.3-1
- Update to 0.9.3

* Tue Mar 20 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.2-4
- Server needs pyOpenSSL

* Wed Feb 28 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.2-3
- Don't forget %%dir

* Wed Feb 28 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.2-2
- Fix #230478

* Mon Feb 19 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.2-1
- Update to 0.9.2

* Thu Feb  8 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.9.1-1.d
- Update to 0.9.1d

* Tue Jan  9 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.3-2
- Merge client back into base package.

* Wed Dec 27 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.3-1
- Update to 0.8.7.3

* Fri Dec 22 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-5
- Server needs client library files too so put them in main package

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-4
- Yes, actually we need to require openssl

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-3
- Don't generate SSL cert in post script, it only needs to be done on
  the server and is handled by the bcfg2-admin tool.
- Move the /etc/bcfg2.key file to the server package
- Don't install a sample copy of the config file, just ghost it
- Require gamin-python for the server package
- Don't require openssl
- Make the client a separate package so you don't have to have the
  client if you don't want it

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-2
- Add more documentation

* Mon Dec 18 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-1
- First version for Fedora Extras
