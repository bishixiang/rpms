# $Id$

# Authority: dag
# Distcc: 0
# Upstream: Kern Sibbald <kern@sibbald.com>
# Upstream: <apcupsd-users@lists.sourceforge.net>

%define _sbindir /sbin

Summary: APC UPS power control daemon.
Name: apcupsd
Version: 3.10.11
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://www.sibbald.com/apcupsd/

Packager: Dag Wieers <dag@wieers.com>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: http://dl.sf.net/apcupsd/apcupsd-%{version}.tar.gz
BuildRoot: %{_tmppath}/root-%{name}-%{version}
Prefix: %{_prefix}

BuildRequires: gd-devel, glibc-devel
Requires: perl

%description
Apcupsd can be used for controlling most APC UPSes. During a power failure,
apcupsd will inform the users about the power failure and that a shutdown
may occur. If power is not restored, a system shutdown will follow when the
battery is exausted, a timeout (seconds) expires, or the battery runtime
expires based on internal APC calculations determined by power consumption
rates. If the power is restored before one of the above shutdown conditions
is met, apcupsd will inform users about this fact.

Some features depend on what UPS model you have (simple or smart).

%prep
%setup

### Add a default apcupsd.conf for Apache.
%{__cat} <<EOF >apcupsd.conf
ScriptAlias /apcupsd/ %{_localstatedir}/www/apcupsd/
<Directory %{_localstatedir}/www/apcupsd/>
        DirectoryIndex upsstats.cgi
        Options ExecCGI
        order deny,allow
        deny from all
        allow from 127.0.0.1
</Directory>
EOF

%build
%configure \
	--sysconfdir="%{_sysconfdir}/apcupsd" \
	--with-cgi-bin="%{_localstatedir}/www/apcupsd" \
	--enable-cgi \
	--enable-pthreads \
	--enable-net \
	--enable-master-slave \
	--enable-apcsmart \
	--enable-dumb \
	--enable-usb
%{__make} %{?_smp_mflags}
%{__make} -C examples hid-ups

%install
%{__rm} -rf %{buildroot}

### FIXME: 'make install' doesn't create sysv-dir and bails out.
%{__install} -d -m0755 %{buildroot}%{_initrddir}
%{__make} install \
	DESTDIR="%{buildroot}"

%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/httpd/conf.d/
%{__install} -m0755 examples/hid-ups examples/make-hiddev %{buildroot}%{_sysconfdir}/apcupsd/
%{__install} -m0644 apcupsd.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/

### Clean up buildroot
%{__rm} -f %{buildroot}%{_initrddir}/halt*

%clean
%{__rm} -rf %{buildroot}

%post
/sbin/chkconfig --add apcupsd

if [ -f %{_sysconfdir}/httpd/conf/httpd.conf ]; then
        if ! grep -q "Include .*/apcupsd.conf" %{_sysconfdir}/httpd/conf/httpd.conf; then
                echo -e "\n# Include %{_sysconfdir}/httpd/conf.d/apcupsd.conf" >> %{_sysconfdir}/httpd/conf/httpd.conf
#               /sbin/service httpd restart
        fi
fi

%preun
if [ $1 -eq 0 ]; then 
        /sbin/service apcuspd stop &>/dev/null || :
        /sbin/chkconfig --del apcupsd
fi

%postun
/sbin/service apcupsd condrestart &>/dev/null || :

%files
%defattr(-, root, root, 0755)
%doc ChangeLog COPYING INSTALL doc/* examples/
%doc %{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/apcupsd/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcupsd.conf
%config %{_initrddir}/*
%{_sbindir}/*
%{_localstatedir}/www/apcupsd/

%changelog
* Sat Mar 06 2004 Dag Wieers <dag@wieers.com> - 3.10.11-1
- Added apcupsd.conf. (Andrew Newman)
- Fixed unsuccessful 'make install'.

* Tue Feb 17 2004 Dag Wieers <dag@wieers.com> - 3.10.11-0
- Initial package. (using DAR)
