%define		database_version 20030621
Summary:	An anti-virus utility for Unix
Summary(pl):	Antywirusowe narzêdzie dla Unixów
Name:		clamav
Version:	0.60
Release:	1
License:	GPL
Group:		Applications
Source0:	http://dl.sourceforge.net/clamav/%{name}-%{version}.tar.gz
# Source0-md5:	eddeba4e1f399f65bc71aa2b3e901543
Source1:	%{name}.init
Source2:	%{name}.sysconfig
# gziped from http://clamav.elektrapro.com/database/:
Source3:	%{name}-database-%{database_version}.tar.gz
# Source3-md5:	26ba23c5a6e6131e1a8efb397e4be9f2
URL:		http://www.clamav.net/
Requires:	%{name}-database
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Clam Antivirus is a powerful anti-virus scanner for Unix. It supports
AMaViS, compressed files, uses the virus database from
OpenAntivirus.org, and includes a program for auto-updating. The
scanner is multithreaded, written in C, and POSIX compliant.

%description -l pl
Clam Antivirus jest potê¿nym skanerem antywirusowym dla systemów
uniksowych. Wspiera on AMaViSa, skompresowane pliki, u¿ywa bazy
wirusów z OpenAntivirus.org, i posiada system automatycznej
aktualizacji. Skaner jest wielow±tkowy, napisany w C i zgodny z
POSIXem.

%package libs
Summary:	Shared libraries for clamav
Summary(pl):	Biblioteki dzielone clamav
Group:		Libraries

%description libs
Shared libraries for clamav.

%description libs -l pl
Biblioteki dzielone clamav.

%package devel
Summary:	clamav - Development header files and libraries
Summary(pl):	clamav - Pliki nag³ówkowe i biblioteki dla programistów
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}

%description devel
This package contains the development header files and libraries
necessary to develop clamav client applications.

%description devel -l pl
Pliki nag³ówkowe i biblioteki konieczne do kompilacji aplikacji
klienckich clamav.

%package static
Summary:	clamav staic libraris
Summary(pl):	Biblioteki statyczne clamav
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}

%description static
clamav static libraris.

%description static -l pl
Biblioteki statyczne clamav.

%package database
Summary:	Virus database for clamav
Summary(pl):	Bazy wirusów dla clamav
Group:		Applications
Version:	%{version}.%{database_version}
Requires:	%{name}

%description database
Virus database for clamav (updated %{database_version})

%description database -l pl
Bazy wirusów dla clamav (aktualizowana %{database_version})

%prep
%setup -q -a 3

%build
rm -f missing
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-clamav \
	--with-dbdir=/var/lib/%{name}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{rc.d/init.d,sysconfig}
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/cron.daily,%{_var}/log}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cat <<EOF >$RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name}
#!/bin/sh
umask 022
%{_bindir}/freshclam --quiet -l %{_var}/log/%{name}.log --daemon-notify
EOF

touch $RPM_BUILD_ROOT%{_var}/log/%{name}.log

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/clamd
install etc/clamav.conf $RPM_BUILD_ROOT%{_sysconfdir}/

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid clamav`" ]; then
        if [ "`getgid clamav`" != "43" ]; then
                echo "Warning: group clamav doesn't have gid=43. Correct this before installing clamav" 1>&2
                exit 1
        fi
else
       echo "Adding group clamav GID=43"
        /usr/sbin/groupadd -g 43 -r -f clamav
fi
if [ -n "`id -u clamav 2>/dev/null`" ]; then
       if [ "`id -u clamav`" != "43" ]; then
               echo "Warning: user clamav doesn't have uid=43. Correct this before installing clamav" 1>&2
               exit 1
       fi
else
       echo "Adding user clamav UID=43"
       /usr/sbin/useradd -u 43 -r -d /tmp  -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav 1>&2
fi

%post
touch %{_var}/log/%{name}.log && chmod 640 %{_var}/log/%{name}.log && chown clamav %{_var}/log/%{name}.log
/sbin/chkconfig --add clamd
if [ -f /var/lock/subsys/clamd ]; then
	/etc/rc.d/init.d/clamd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/clamd start\" to start Clam Antivirus daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/clamd ]; then
		/etc/rc.d/init.d/clamd stop
	fi
	/sbin/chkconfig --del clamd
fi

%postun
if [ "$1" = "0" ]; then
       echo "Removing user clamav"
       /usr/sbin/userdel clamav
       echo "Removing group clamav"
       /usr/sbin/groupdel clamav
fi

%post   libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS README TODO docs/html/
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(755,clamav,root) %dir /var/lib/%{name}
%attr(640,clamav,root) %ghost %{_var}/log/%{name}.log
%attr(750,root,root) %{_sysconfdir}/cron.daily/%{name}
%attr(644,root,root) %config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/*.conf
%attr(754,root,root) /etc/rc.d/init.d/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/clamd
%{_mandir}/man?/*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/*.h

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a

%files database
%defattr(644,root,root,755)
%attr(644,clamav,root) %verify(not md5 size mtime) /var/lib/%{name}/*.db*
%attr(644,clamav,root) %verify(not md5 size mtime) /var/lib/%{name}/mirrors.txt
