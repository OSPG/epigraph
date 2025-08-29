#!/bin/sh
OWNER=gentoo
REPO=gentoo
FILEOUT=issues.json

printf 'downloading all issues from github:%s/%s\n' "${OWNER}" "${REPO}"
printf 'note that this might take some time... (~5 minutes)\n'
start=$(date +%s)

tmpout="$(mktemp)"
gh api -X GET \
	repos/"$OWNER"/"$REPO"/issues \
	--paginate -f state=all -f per_page=100 \
	> "${tmpout}"
errno=$?
[ $errno -eq 0 ] || { printf 'huh, failed to download issues. :(\n' >&2; exit $errno; }

if [ -e "${FILEOUT}" ]; then
	printf '%s already existed. deleting in 5s. abort with ^C\n' "${FILEOUT}" >&2
	sleep 5s
	rm "${FILEOUT}"
fi
mv "${tmpout}" "${FILEOUT}"

total_time=$(($(date +%s) - start))
printf "done! completed after %s seconds\n" ${total_time}
printf "file is located in %s\n" "${FILEOUT}"

