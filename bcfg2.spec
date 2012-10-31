%if (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif
%{!?py_ver: %define py_ver %(%{__python} -c 'import sys;print(sys.version[0:3])')}
%global pythonversion %{py_ver}
#%global _rc 1
%global _pre 2

Name:             bcfg2
Version:          1.3.0
#Release:          1%{?dist}
#Release:          0.1%{?_rc:.rc%{_rc}}%{?dist}
Release:          0.1%{?_pre:.pre%{_pre}}%{?dist}
Summary:          A configuration management system

Group:            Applications/System
License:          BSD
URL:              http://bcfg2.org
#Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}.tar.gz
#Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}.tar.gz.gpg
#Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz
#Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz.gpg
Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_pre:pre%{_pre}}.tar.gz
Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_pre:pre%{_pre}}.tar.gz.gpg
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

BuildRequires:    python2-devel
BuildRequires:    python-setuptools

Requires:         python-lxml
Requires:         python-nose
%if 0%{?epel} > 0
Requires:	      python-ssl
%endif

%if 0%{?fedora} >= 16
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(postun): /sbin/service
%endif

%description
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to Bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

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
%if 0%{?fedora} >= 16
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(post):   systemd-sysv
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(postun): /sbin/service
%endif

%description server
Configuration management server

%package web
Summary:          Bcfg2 Web Reporting Interface
Group:            System

Requires:         bcfg2-server
Requires:         httpd
Requires:         Django
%if "%{_vendor}" == "redhat"
Requires: mod_wsgi
%define apache_conf %{_sysconfdir}/httpd
%else
Requires: apache2-mod_wsgi
%define apache_conf %{_sysconfdir}/apache2
%endif

%description web
The Bcfg2 Web Reporting Interface.

%package doc
Summary:          Documentation for Bcfg2
Group:            System

BuildRequires:    python-sphinx
BuildRequires:    python-docutils

%description doc
Documentation for Bcfg2.

%package examples
Summary:          Examples for Bcfg2
Group:            System

%description examples
Examples files for Bcfg2.

%prep
#%setup -q
#%setup -q -n %{name}-%{version}%{?_rc:rc%{_rc}}
%setup -q -n %{name}-%{version}%{?_pre:pre%{_pre}}

# Fixup some paths
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' debian/bcfg2.init
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' debian/bcfg2-server.init
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' tools/bcfg2-cron

%{__perl} -pi -e 's@/usr/lib/bcfg2@%{_libexecdir}@g' debian/bcfg2.cron.daily
%{__perl} -pi -e 's@/usr/lib/bcfg2@%{_libexecdir}@g' debian/bcfg2.cron.hourly

# Don't start servers by default
%{__perl} -pi -e 's@chkconfig: (\d+)@chkconfig: -@' debian/bcfg2.init
%{__perl} -pi -e 's@chkconfig: (\d+)@chkconfig: -@' debian/bcfg2-server.init

# Get rid of extraneous shebangs
for f in `find src/lib -name \*.py`
do
    %{__sed} -i -e '/^#!/,1d' $f
done

%build
%{__python} setup.py build
#%{__python} setup.py build_dtddoc
%{__python} setup.py build_sphinx

#%{?pythonpath: export PYTHONPATH="%{pythonpath}"}
#%{__python}%{pythonversion} setup.py build_dtddoc
#%{__python}%{pythonversion} setup.py build_sphinx

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}

mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/cron.daily
mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_var}/lib/bcfg2
mkdir -p %{buildroot}%{_var}/cache/bcfg2

mv %{buildroot}%{_bindir}/bcfg2* %{buildroot}%{_sbindir}

install -m 755 debian/bcfg2.init %{buildroot}%{_initrddir}/bcfg2
install -m 755 debian/bcfg2-server.init %{buildroot}%{_initrddir}/bcfg2-server
install -m 755 debian/bcfg2.cron.daily %{buildroot}%{_sysconfdir}/cron.daily/bcfg2
install -m 755 debian/bcfg2.cron.hourly %{buildroot}%{_sysconfdir}/cron.hourly/bcfg2
install -m 755 tools/bcfg2-cron %{buildroot}%{_libexecdir}/bcfg2-cron

install -m 644 debian/bcfg2.default %{buildroot}%{_sysconfdir}/sysconfig/bcfg2
install -m 644 debian/bcfg2-server.default %{buildroot}%{_sysconfdir}/sysconfig/bcfg2-server

touch %{buildroot}%{_sysconfdir}/%{name}.{cert,conf,key}

# systemd
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 redhat/systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -m 644 redhat/systemd/%{name}-server.service %{buildroot}%{_unitdir}/%{name}-server.service

# Webserver
install -d %{buildroot}%{apache_conf}/conf.d
install -p -m 644 misc/apache/bcfg2.conf %{buildroot}%{apache_conf}/conf.d/wsgi_bcfg2.conf

# Documentation
#mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}
#mv build/sphinx/html/* %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}
mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}
mv build/sphinx/html/* %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}
#mv build/dtd %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}/

# Examples
#mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-examples-%{version}
#mv examples %{buildroot}%{_defaultdocdir}/bcfg2-examples-%{version}/
mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-examples-%{version}%{?_pre:pre%{_pre}}
mv examples %{buildroot}%{_defaultdocdir}/bcfg2-examples-%{version}%{?_pre:pre%{_pre}}/

%clean
rm -rf %{buildroot}

%post
%if 0%{?fedora} >= 18
  %systemd_post bcfg2.service
%else
  if [ $1 -eq 1 ] ; then
      # Initial installation
  %if 0%{?fedora} >= 16
      /bin/systemctl daemon-reload >/dev/null 2>&1 || :
  %else
      /sbin/chkconfig --add bcfg2
  %endif
  fi
%endif

%post server
%if 0%{?fedora} >= 18
  %systemd_post bcfg2-server.service
%else
  if [ $1 -eq 1 ] ; then
      # Initial installation
  %if 0%{?fedora} >= 16
      /bin/systemctl daemon-reload >/dev/null 2>&1 || :
  %else
      /sbin/chkconfig --add bcfg2-server
  %endif
  fi
%endif

%preun
%if 0%{?fedora} >= 18
  %systemd_preun bcfg2.service
%else
  if [ $1 -eq 0 ]; then
      # Package removal, not upgrade
  %if 0%{?fedora} >= 16
      /bin/systemctl --no-reload disable bcfg2.service > /dev/null 2>&1 || :
      /bin/systemctl stop bcfg2.service > /dev/null 2>&1 || :
  %else
      /sbin/service bcfg2 stop &>/dev/null || :
      /sbin/chkconfig --del bcfg2
  %endif
  fi
%endif

%preun server
%if 0%{?fedora} >= 18
  %systemd_preun bcfg2-server.service
%else
  if [ $1 -eq 0 ]; then
      # Package removal, not upgrade
  %if 0%{?fedora} >= 16
      /bin/systemctl --no-reload disable bcfg2-server.service > /dev/null 2>&1 || :
      /bin/systemctl stop bcfg2-server.service > /dev/null 2>&1 || :
  %else
      /sbin/service bcfg2-server stop &>/dev/null || :
      /sbin/chkconfig --del bcfg2-server
  %endif
  fi
%endif

%postun
%if 0%{?fedora} >= 18
  %systemd_postun bcfg2.service
%else
  %if 0%{?fedora} >= 16
  /bin/systemctl daemon-reload >/dev/null 2>&1 || :
  %endif
  if [ $1 -ge 1 ] ; then
      # Package upgrade, not uninstall
  %if 0%{?fedora} >= 16
      /bin/systemctl try-restart bcfg2.service >/dev/null 2>&1 || :
  %else
      /sbin/service bcfg2 condrestart &>/dev/null || :
  %endif
  fi
%endif

%postun server
%if 0%{?fedora} >= 18
  %systemd_postun bcfg2-server.service
%else
  %if 0%{?fedora} >= 16
  /bin/systemctl daemon-reload >/dev/null 2>&1 || :
  %endif
  if [ $1 -ge 1 ] ; then
      # Package upgrade, not uninstall
  %if 0%{?fedora} >= 16
      /bin/systemctl try-restart bcfg2-server.service >/dev/null 2>&1 || :
  %else
      /sbin/service bcfg2-server condrestart &>/dev/null || :
  %endif
  fi
%endif

%triggerun -- bcfg2 < 1.2.1-1
/usr/bin/systemd-sysv-convert --save bcfg2 >/dev/null 2>&1 || :
/bin/systemctl --no-reload enable bcfg2.service >/dev/null 2>&1 || :
/sbin/chkconfig --del bcfg2 >/dev/null 2>&1 || :
/bin/systemctl try-restart bcfg2.service >/dev/null 2>&1 || :

%triggerun server -- bcfg2-server < 1.2.1-1
/usr/bin/systemd-sysv-convert --save bcfg2-server >/dev/null 2>&1 || :
/bin/systemctl --no-reload enable bcfg2-server.service >/dev/null 2>&1 || :
/sbin/chkconfig --del bcfg2-server >/dev/null 2>&1 || :
/bin/systemctl try-restart bcfg2-server.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYRIGHT README
%{_mandir}/man1/bcfg2.1*
%{_mandir}/man5/bcfg2*.5*
%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.cert
%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.conf
%if 0%{?fedora} >= 16
    %config(noreplace) %{_unitdir}/%{name}.service
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/bcfg2
%{_sysconfdir}/cron.daily/bcfg2
%{_sysconfdir}/cron.hourly/bcfg2
%{_initrddir}/bcfg2
%{_sbindir}/bcfg2
%{_libexecdir}/bcfg2-cron
%dir %{_var}/cache/bcfg2
%{python_sitelib}/Bcfg2*.egg-info
%dir %{python_sitelib}/Bcfg2
%{python_sitelib}/Bcfg2/__init__.*
%{python_sitelib}/Bcfg2/Client
%{python_sitelib}/Bcfg2/Logger.*
%{python_sitelib}/Bcfg2/Options.*
%{python_sitelib}/Bcfg2/Proxy.*
%{python_sitelib}/Bcfg2/SSLServer.*
%{python_sitelib}/Bcfg2/Statistics.*

%files server
%defattr(-,root,root,-)
%{_mandir}/man8/bcfg2*.8*
%ghost %attr(600,root,root) %config(noreplace) %{_sysconfdir}/bcfg2.key
%if 0%{?fedora} >= 16
    %config(noreplace) %{_unitdir}/%{name}-server.service
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/bcfg2-server
%{_initrddir}/bcfg2-server
%{_datadir}/bcfg2
%{_sbindir}/bcfg2-*
%dir %{_var}/lib/bcfg2
%{python_sitelib}/Bcfg2/Server

%files web
%defattr(-,root,root,-)
%{_datadir}/bcfg2/reports.wsgi
%{_datadir}/bcfg2/site_media
%config(noreplace) %{apache_conf}/conf.d/wsgi_bcfg2.conf

%files doc
%defattr(-,root,root,-)
#%doc %{_defaultdocdir}/bcfg2-doc-%{version}
%doc %{_defaultdocdir}/bcfg2-doc-%{version}%{?_pre:pre%{_pre}}
#%doc %{_defaultdocdir}/bcfg2-doc-%{version}%{?_rc:rc%{_rc}}

%files examples
%defattr(-,root,root,-)
#%doc %{_defaultdocdir}/bcfg2-examples-%{version}
%doc %{_defaultdocdir}/bcfg2-examples-%{version}%{?_pre:pre%{_pre}}
#%doc %{_defaultdocdir}/bcfg2-examples-%{version}%{?_rc:rc%{_rc}}

%changelog
* Wed Oct 31 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.3.0-0.1.pre2
- Updated to new upstream version 1.3.0 pre2

* Mon Aug 27 2012 Václav Pavlín <vpavlin@redhat.com> - 1.2.3-3
- Scriptlets replaced with new systemd macros (#850043)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jul 07 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.3-1
- Fix CVE-2012-3366
- Updated to new upstream version 1.2.3

* Tue May 01 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.2-2
- python-nose is needed by bcfg2-test

* Fri Apr 06 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.2-1
- Updated to new upstream version 1.2.2

* Sun Feb 26 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.1-2
- Fixed systemd files

* Tue Feb 07 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.1-1
- Added examples package
- Updated to new upstream version 1.2.1

* Mon Jan 02 2012 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-6
- Added support for systemd
- Example subpackage

* Wed Sep 07 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-5
- Updated to new upstreadm version 1.2.0

* Wed Sep 07 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-4.1.rc1
- Updated to new upstreadm version 1.2.0rc1

* Wed Jun 22 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-3.1.pre3
- Updated to new upstreadm version 1.2.0pre3

* Wed May 04 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-2.1.pre2
- Added bcfg2-lint stuff
- Pooled file section entries to reduce future maintainance
- Removed Patch

* Wed May 04 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-1.1.pre2
- Updated to new upstream version 1.2.0pre2

* Sun Mar 20 2011 Fabian Affolter <mail@fabian-affolter.ch> - 1.2.0-1.1.pre1
- Added doc subpackage
- Updated to new upstream version 1.2.0pre1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Nov 18 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.1-2
- Added new man page
- Updated doc section (ChangeLog is gone)

* Thu Nov 18 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.1-1
- Updated to new upstream version 1.1.1

* Fri Nov  5 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-3
- Add patch from Gordon Messmer to fix authentication on F14+ (Python 2.7)

* Mon Sep 27 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-2
- Update to final version

* Wed Sep 15 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-1.3.rc5
- Update to 1.1.0rc5:

* Tue Aug 31 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-1.2.rc4
- Add new YUMng driver

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.1.0-1.1.rc4.1
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 20 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.0-1.1.rc4
- Added patch to fix indention

* Tue Jul 20 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.0-0.1.rc4
- Updated to new upstream release candidate RC4

* Sat Jun 19 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.0-0.1.rc3
- Updated to new upstream release candidate RC3 

* Sun May 02 2010 Fabian Affolter <mail@fabian-affolter.ch> - 1.1.0-0.2.rc1
- Changed define to global
- Added graphviz for the server package

* Wed Apr 28 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.1.0-0.1.rc1
- Update to 1.1.0rc1

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
