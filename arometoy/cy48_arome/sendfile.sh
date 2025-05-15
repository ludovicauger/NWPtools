#!/bin/bash
ftp lxgmap47.cnrm.meteo.fr<<EOF
cd tmploc
put ICMSHFCST+0001
bye
EOF
