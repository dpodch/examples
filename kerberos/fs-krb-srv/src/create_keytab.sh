ERROR ()
{
	cd $PWD
	echo ERROR: $*
	exit 1
}

SLEEP_MS=${REBUILD_KEYTAB_SEC:-86400}

[ "${DOMAIN_USER}" == "" ] && ERROR "not set DOMAIN_USER"
[ "${DOMAIN_USER_PASSWD}" == "" ] && ERROR "not set DOMAIN_USER_PASSWD"
[ "${KEYTAB_PATH}" == "" ] && ERROR "not set KEYTAB_PATH"

while true
do
  rm -f ${KEYTAB_PATH} || :
  printf "%b" "addent -password -p ${DOMAIN_USER} -k 6 -e RC4-HMAC\n${DOMAIN_USER_PASSWD}\nwrite_kt ${KEYTAB_PATH}" | ktutil
  klist -ket ${KEYTAB_PATH}
  [ $? != "0" ] && ERROR "create ${KEYTAB_PATH}"
  sleep ${SLEEP_MS}
done