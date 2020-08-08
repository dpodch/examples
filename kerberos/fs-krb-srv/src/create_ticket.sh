ERROR ()
{
	cd $PWD
	echo ERROR: $*
	exit 1
}

SLEEP_MS=${REBUILD_TICKET_SEC:-86400}

[ "${KEYTAB_PATH}" == "" ] && ERROR "not set KEYTAB_PATH"
[ "${TICKET_PATH}" == "" ] && ERROR "not set TICKET_PATH"
[ "${DOMAIN_USER_PRINCIPAL}" == "" ] && ERROR "not set DOMAIN_USER_PRINCIPAL"

while true
do
  /usr/bin/kinit -V -t ${KEYTAB_PATH} -c ${TICKET_PATH} ${DOMAIN_USER_PRINCIPAL}
  [ $? != "0" ] && ERROR "create ticket: ${TICKET_PATH}"
  sleep ${SLEEP_MS}
done




