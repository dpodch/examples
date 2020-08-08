#!/bin/sh

DEBBUILD=~/debbuild
NPR=fs-krb-srv
OLD_PWD=`pwd`

ERROR ()
{
	cd $PWD
	echo ERROR: $*
	exit 1
}


IS_ASTRALINUX=`(test -e /etc/astra_version && echo 1 || echo 0)`
if [ $IS_ASTRALINUX -ge 1 ] ; then
	echo "AstraLinux BUILDING"
	ASTRABUILD="--nodeps"
fi


make_rpm()
{
	find ~/rpmbuild/ -name "$NPR*" -type d | xargs rm -rf
	find ~/rpmbuild/RPMS -name "$NPR*.rpm" -type f | xargs rm -rf

#	выдёргиваем версию пакета
	VER_MAJOR=`cat $NPR.spec | grep "define" | grep "version_major" | awk '{print $3}'`
	VER_MINOR=`cat $NPR.spec | grep "define" | grep "version_minor" | awk '{print $3}'`
	VER_PATCH=`cat $NPR.spec | grep "define" | grep "version_patch" | awk '{print $3}'`
	VER_BUILD=`cat $NPR.spec | grep "define" | grep "version_build" | awk '{print $3}'`

	VERSIONSTR=$VER_MAJOR.$VER_MINOR.$VER_PATCH
	VERSION_FULL="$VERSIONSTR-$VER_BUILD"

	DSTDIR=/var/tmp/${NPR}  #  временная директория с архивом файлов пакета
	PROGRAM=${NPR}-${VERSIONSTR}	# название пакета - имя и версия

#	название архива файлов пакета
	ANAME="${DSTDIR}/${PROGRAM}.tgz"

	RPM_BASE_NAME=`grep "%define.*name" $NPR.spec | awk '{print $3}'`
	echo "RPM_BASE_NAME = $RPM_BASE_NAME"

	RPM_EXT_NAMES=`grep "%package.*n" $NPR.spec   | awk '{print $3}' | sed "s/%{name}/$RPM_BASE_NAME/g"`
	echo "RPM_EXT_NAMES = $RPM_EXT_NAMES"

	ALL_BUILD_RPMS="$RPM_BASE_NAME
	$RPM_EXT_NAMES"

	#	очистка рабочих каталогов
	rm -Rf ${DSTDIR}
	mkdir ${DSTDIR}
	mkdir ${DSTDIR}/${PROGRAM}

	# очистка каталога исходников
	if [ "$EXPORT_SRC_DIR" != "" ]; then
		rm -rf ~/rpmbuild/BUILD
	fi

	cp -prf ../src \
		systemd \
		$NPR.spec \
		${DSTDIR}/${PROGRAM} \
		|| 	ERROR "Cannot copy to ${DSTDIR}/${PROGRAM}"

	cd ${DSTDIR} || ERROR "Cannot cd to ${DSTDIR}"

	rm -rf `find . | grep .svn` || ERROR "Cannot remove svn dir"

	tar cfz $ANAME ${PROGRAM} || ERROR "Creating tar"

	rpmbuild -tb $ANAME $ASTRABUILD || ERROR "building rpm"

	cd $OLD_PWD
	# уничтожение временных файлов
	rm -Rf ${DSTDIR}
	rm -rf ${DEBBUILD} || ERROR "remove ${DEBBUILD} directory"
	mkdir ${DEBBUILD} || ERROR "create ${DEBBUILD} directory"

	# при сборке deb версия build увеличивается на 1
	#let "INC=VER_BUILD+1"
	let "INC=VER_BUILD"
	if [ -f /opt/forsys/distribution/build_utils/deb_exists.inc.sh ] ; then
			source /opt/forsys/distribution/build_utils/deb_exists.inc.sh
			DEB_STR=$rpm\_$VERSIONSTR\-$INC
			DEB_EXISTS=`is_deb_exists $DEB_STR`
	fi

	if [ $IS_ASTRALINUX -ge 1 ] && [ "$DEB_EXISTS" != "yes" ]; then
		echo "AstraLinux BUILDING deb"
		
		for rpm in $ALL_BUILD_RPMS ; do
			rpm_full_name=`find ~/rpmbuild/ -type f -name "$rpm-$VERSION_FULL*.rpm"`

            if [ "$rpm_full_name" = "" ] ; then
                    ERROR "RPM for $rpm not FOUINT in ~/rpmbuild"
            fi

            echo "Building DEB for $rpm_full_name ..."
            if [ ! -f $rpm_full_name ] ; then
                    ERROR "RPM $rpm_full_name not FOUND"
            fi

            alien -k -s --generate --scripts $rpm_full_name || ERROR "alien for $rpm_full_name"

			# add debian req
			deb_req=`grep "%define AstraLinuxRequires_$rpm:" $NPR.spec | sed 's/%define//g' | sed "s/AstraLinuxRequires_$rpm://g"`
			echo "deb_req = $deb_req"
			sed -i "s/Depends:.*/Depends: \$\{shlibs:Depends\},$deb_req/" $rpm-$VERSIONSTR/debian/control	
		
			deb_obs=`grep "%define AstraLinuxObsoletes_$rpm:" $NPR.spec | sed 's/%define//g' | sed "s/AstraLinuxObsoletes_$rpm://g"`
			echo "deb_obs = $deb_obs"

			if grep -q "Conflicts:" $rpm-$VERSIONSTR/debian/control ; then
				sed -i "s/Conflicts:.*/Conflicts: $deb_obs/" $rpm-$VERSIONSTR/debian/control
			else
				echo "Conflicts: $deb_obs" >> $rpm-$VERSIONSTR/debian/control
			fi

			if grep -q "Replaces:" $rpm-$VERSIONSTR/debian/control ; then
				sed -i "s/Replaces:.*/Replaces: $deb_obs/" $rpm-$VERSIONSTR/debian/control
			else
				echo "Replaces: $deb_obs" >> $rpm-$VERSIONSTR/debian/control
			fi

			cd $rpm-$VERSIONSTR
			dpkg-buildpackage -uc -us || ERROR "dpkg-buildpackage"
			
			cd ..
			rm -rf $rpm-$VERSIONSTR $rpm-$VERSIONSTR.orig

			find . -name $rpm"_*" | grep "$VERSIONSTR" | grep -v deb | xargs rm -rfv

			FILENAME=`find . -name $rpm"_*" | grep "$VERSION" | grep deb | head --lines=1`
			mv -fv $FILENAME ${DEBBUILD}/
		done
	fi
}

make_rpm
