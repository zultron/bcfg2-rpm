%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

#define _rc 4

Name:             bcfg2
Version:          1.0.0
Release:          1%{?_rc:.rc%{_rc}}%{?dist}
Summary:          Configuration management system

Group:            Applications/System
License:          BSD
URL:              http://trac.mcs.anl.gov/projects/bcfg2
Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz
Source1:          ftp://ftp.mcs.anl.gov/pub/bcfg/bcfg2-%{version}%{?_rc:rc%{_rc}}.tar.gz.gpg

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:        noarch

%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif

Requires:         python-lxml
%if 0%{?epel} > 0
Requires:	  python-ssl
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
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(postun): /sbin/service

%description server
Configuration management server

%prep
%setup -q -n %{name}-%{version}%{?_rc:rc%{_rc}}

# fixup some paths
%{__perl} -pi -e 's@/etc/default@%{_sysconfdir}/sysconfig@g' debian/bcfg2.init
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

mv %{buildroot}%{_bindir}/bcfg2* %{buildroot}%{_sbindir}

install -m 755 debian/bcfg2.init %{buildroot}%{_initrddir}/bcfg2
install -m 755 debian/bcfg2-server.init %{buildroot}%{_initrddir}/bcfg2-server
install -m 755 debian/bcfg2.cron.daily %{buildroot}%{_sysconfdir}/cron.daily/bcfg2
install -m 755 debian/bcfg2.cron.hourly %{buildroot}%{_sysconfdir}/cron.hourly/bcfg2
install -m 755 tools/bcfg2-cron %{buildroot}%{_libexecdir}/bcfg2-cron

install -m 644 debian/bcfg2.default %{buildroot}%{_sysconfdir}/sysconfig/bcfg2

touch %{buildroot}%{_sysconfdir}/bcfg2.cert
touch %{buildroot}%{_sysconfdir}/bcfg2.conf
touch %{buildroot}%{_sysconfdir}/bcfg2.key

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
%doc AUTHORS ChangeLog examples COPYRIGHT README

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
%{_mandir}/man8/bcfg2-server.8*

%dir %{_var}/lib/bcfg2

%changelog
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
