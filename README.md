# pptpd

Forked version of pptpd with ClearOS changes applied

* git clone git+ssh://git@github.com/clearos/pptpd.git
* cd pptpd
* git checkout epel7
* git remote add upstream git://pkgs.fedoraproject.org/pptpd.git
* git pull upstream epel7
* git checkout clear7
* git merge --no-commit epel7
* git commit
