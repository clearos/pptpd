# Available rpmbuild options:
#
# --without	libwrap
# --without	bcrelay
#

# hardened build if not overriden
%{!?_hardened_build:%global _hardened_build 1}

%if %{?_hardened_build:%{_hardened_build}}%{!?_hardened_build:0}
%global harden -Wl,-z,relro,-z,now
%endif

Summary:	PoPToP Point to Point Tunneling Server
Name:		pptpd
Version:	1.4.0
Release:	5%{?dist}
License:	GPLv2+ and LGPLv2+
Group:		Applications/Internet
BuildRequires:	ppp-devel, systemd
URL:		http://poptop.sourceforge.net/
Source0:	http://downloads.sf.net/poptop/pptpd-%{version}.tar.gz
Source1:	pptpd.service
Source2:	pptpd.sysconfig
%global pppver %((%{__awk} '/^#define VERSION/ { print $NF }' /usr/include/pppd/patchlevel.h 2>/dev/null||echo none)|/usr/bin/tr -d '"')
Requires:	ppp = %{pppver}
Requires:	perl

%if %{?_without_libwrap:0}%{!?_without_libwrap:1}
BuildRequires:	tcp_wrappers-devel
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
This implements a Virtual Private Networking Server (VPN) that is
compatible with Microsoft VPN clients. It allows windows users to
connect to an internal firewalled network using their dialup.

%package sysvinit
Summary: PoPToP Point to Point Tunneling Server
Group: Applications/Internet
BuildArch: noarch
Requires: %{name} = %{version}-%{release}
Requires(preun): /sbin/service

%description sysvinit
The SysV initscript for PoPToP Point to Point Tunneling Server.

%prep
%setup -q

# Fix for distros with %%{_libdir} = /usr/lib64
perl -pi -e 's,/usr/lib/pptpd,%{_libdir}/pptpd,;' pptpctrl.c

%build
%configure \
	%{!?_without_libwrap:--with-libwrap} \
	%{?_without_libwrap:--without-libwrap} \
	%{!?_without_bcrelay:--enable-bcrelay} \
	%{?_without_bcrelay:--disable-bcrelay}
(echo '#undef VERSION'; echo '#include <pppd/patchlevel.h>') >> plugins/patchlevel.h
make CFLAGS='-fno-builtin -fPIC -DSBINDIR=\"%{_sbindir}\" %{optflags} %{?harden}'

%install
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_sysconfdir}/ppp
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man{5,8}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

make %{?_smp_mflags} \
	DESTDIR=%{buildroot} \
	INSTALL="install -p" \
	LIBDIR=%{buildroot}%{_libdir}/pptpd \
	install
install -pm 0755 pptpd.init %{buildroot}%{_sysconfdir}/rc.d/init.d/pptpd
install -pm 0644 samples/pptpd.conf %{buildroot}%{_sysconfdir}/pptpd.conf
install -pm 0644 samples/options.pptpd %{buildroot}%{_sysconfdir}/ppp/options.pptpd
install -pm 0755 tools/vpnuser %{buildroot}%{_bindir}/vpnuser
install -pm 0755 tools/vpnstats.pl %{buildroot}%{_bindir}/vpnstats.pl
install -pm 0755 tools/pptp-portslave %{buildroot}%{_sbindir}/pptp-portslave
install -pm 0644 pptpd.conf.5 %{buildroot}%{_mandir}/man5/pptpd.conf.5
install -pm 0644 pptpd.8 %{buildroot}%{_mandir}/man8/pptpd.8
install -pm 0644 pptpctrl.8 %{buildroot}%{_mandir}/man8/pptpctrl.8
install -pm 0644 %{SOURCE1} %{buildroot}%{_unitdir}
install -pm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/pptpd

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%post sysvinit
/sbin/chkconfig --add pptpd >/dev/null 2>&1 ||:

%preun sysvinit
if [ "$1" = 0 ]; then
    %{_initrddir}/pptpd stop >/dev/null 2>&1 ||:
    /sbin/chkconfig --del pptpd >/dev/null 2>&1 ||:
fi

%postun sysvinit
[ "$1" -ge 1 ] && %{_initrddir}/pptpd condrestart >/dev/null 2>&1 ||:

%files
%doc AUTHORS COPYING README* TODO ChangeLog* samples
%{_sbindir}/pptpd
%{_sbindir}/pptpctrl
%{_sbindir}/pptp-portslave
%{!?_without_bcrelay:%{_sbindir}/bcrelay}
%dir %{_libdir}/pptpd
%{_libdir}/pptpd/pptpd-logwtmp.so
%{_bindir}/vpnuser
%{_bindir}/vpnstats.pl
%{_mandir}/man5/pptpd.conf.5*
%{_mandir}/man8/*.8*
%{_unitdir}/pptpd.service
%config(noreplace) %{_sysconfdir}/sysconfig/pptpd
%config(noreplace) %{_sysconfdir}/pptpd.conf
%config(noreplace) %{_sysconfdir}/ppp/options.pptpd

%files sysvinit
%attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/pptpd

%changelog
* Wed Aug 13 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 1.4.0-5
- Rebuilt for new ppp

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 11 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 1.4.0-3
- Rebuilt for new ppp

* Mon Nov 11 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 1.4.0-2
- Fixed license tag
  Related: rhbz#632853

* Fri Oct 25 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 1.4.0-1
- New version
- Dropped pppd-unbundle patch (upstreamed)

* Tue Oct 22 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 1.3.4-4
- Various fixes according to Fedora review
  Related: rhbz#632853

* Fri Oct 18 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 1.3.4-3
- Modified for Fedora
  Resolves: rhbz#632853

* Fri May 21 2010 Paul Howarth <paul@city-fan.org> - 1.3.4-2
- Define RPM macros in global scope
- Clarify license as GPL version 2 or later
- Add betabuild suffix to dist tag

* Fri Apr 20 2007 Paul Howarth <paul@city-fan.org> - 1.3.4-1.1
- Rebuild against ppp 2.4.4

* Fri Apr 20 2007 Paul Howarth <paul@city-fan.org> - 1.3.4-1
- Update to 1.3.4
- Use downloads.sf.net URL instead of dl.sf.net for source
- Use "install -p" to try to preserve upstream timestamps
- Remove bsdppp and slirp build options (package requires standard ppp)
- Remove ipalloc build option (not supported by upstream configure script)
- Use enable/disable rather than with/without for bcrelay configure option

* Wed Jan 10 2007 Paul Howarth <paul@city-fan.org> - 1.3.3-2
- Use file-based build dependency on /usr/include/tcpd.h instead of
  tcp_wrappers package, since some distributions have this file in
  tcp_wrappers-devel
- Set VERSION using pppd's patchlevel.h rather than using the constant "2.4.3"
- Buildrequire /usr/include/pppd/patchlevel.h (recent-ish pppd)
- Add dependency on the exact version of ppp that pptpd is built against
- Use tabs rather than spaces for indentation

* Tue Sep  5 2006 Paul Howarth <paul@city-fan.org> - 1.3.3-1
- Update to 1.3.3
- Add dist tag
- Add %%postun scriptlet dependency for /sbin/service
- Fix doc permissions

* Fri Mar 31 2006 Paul Howarth <paul@city-fan.org> - 1.3.1-1
- Update to 1.3.1

* Fri Mar 31 2006 Paul Howarth <paul@city-fan.org> - 1.3.0-1
- update to 1.3.0
- remove redundant macro definitions
- change Group: to one listed in rpm's GROUPS file
- use full URL for source
- simplify conditional build code
- use macros for destination directories
- honour %%{optflags}
- general spec file cleanup
- initscript updates:
	don't enable the service by default
	add reload and condrestart options
- condrestart service on package upgrade
- fix build on x86_64
- add buildreq tcp_wrappers

* Fri Feb 18 2005 James Cameron <james.cameron@hp.com>
- fix to use ppp 2.4.3 for plugin

* Thu Nov 11 2004 James Cameron <james.cameron@hp.com>
- adjust for building on Red Hat Enterprise Linux, per Charlie Brady
- remove vpnstats, superceded by vpnstats.pl

* Fri May 21 2004 James Cameron <james.cameron@hp.com>
- adjust for packaging naming and test

* Fri Apr 23 2004 James Cameron <james.cameron@hp.com>
- include vpnwho.pl

* Thu Apr 22 2004 James Cameron <james.cameron@hp.com>
- change description wording
- change URL for upstream
- release first candidate for 1.2.0

* Fri Jul 18 2003 R. de Vroede <richard@oip.tudelft.nl>
- Check the ChangeLog files.

