#!/bin/sh
OWNER=gentoo
REPO=gentoo
FILEOUT=issues.json

exec \
gh api -X GET \
	repos/"$OWNER"/"$REPO"/issues \
	--paginate -f state=all -f per_page=100 \
	> "${FILEOUT}"

