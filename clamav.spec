Summary:	A Mail Virus Scanner
Summary(pl):	Antywirusowy skaner poczty elektronicznej
Name:		clamav
Version:	0.14
Release:	1
License:	GPL
Group:		Applications/Mail
Source0:	http://www.konarski.edu.pl/~zolw/clam/%{name}-%{version}.tar.gz
URL:		http://www.konarski.edu.pl/~zolw/clam.html
BuildRequires:	autoconf
BuildRequires:	automake
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

%prep
%setup -q

%build
rm -f missing
aclocal
%{__autoconf}
%{__automake}
%configure \
	--disable-clamav
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/cron.daily,%{_var}/log}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo -e '#!/bin/sh\n%{_bindir}/freshclam --quiet -l %{_var}/log/%{name}.log' \
	> $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name}

touch $RPM_BUILD_ROOT%{_var}/log/%{name}.log

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid clamav`" ]; then
        if [ "`getgid clamav`" != "43" ]; then
                echo "Warning: group clamav doesn't have gid=43. Correct this before installing clamav" 1>&2
                exit 1
        fi
else
        /usr/sbin/groupadd -g 43 -r -f clamav
fi
if [ -n "`id -u clamav 2>/dev/null`" ]; then
	if [ "`id -u clamav`" != "43" ]; then
		echo "Warning: user clamav doesn't have uid=43. Correct this before installing clamav" 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 43 -r -d /tmp  -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav 1>&2
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel clamav
	/usr/sbin/groupdel clamav
fi

%post
touch %{_var}/log/%{name}.log && chmod 640 %{_var}/log/%{name}.log && chown clamav %{_var}/log/%{name}.log

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS README TODO docs/*.pdf
%attr(755,root,root) %{_bindir}/*
%attr(755,clamav,root) %dir %{_datadir}/%{name}
%attr(644,clamav,root) %verify(not md5 size mtime) %{_datadir}/%{name}/*.db
%attr(640,clamav,root) %ghost %{_var}/log/%{name}.log
%attr(750,root,root) %{_sysconfdir}/cron.daily/%{name}
%{_mandir}/man?/*
