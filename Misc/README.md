# **Zombie** (50 pts, 385 solves)

## **Description**
Oh, shoot, I could have sworn there was a flag here. Maybe it's still alive out there?


## **Solution**

Upon logging in, we can see a file called `.user-entrypoint.sh` in the current directory.

```console
user@zombie:~$ ls -la
total 24
drwxr-sr-x    1 user     user          4096 Jun 18 10:27 .
drwxr-xr-x    1 root     root          4096 Jun 14 17:52 ..
-rwxr-xr-x    1 user     user          3846 Jun 14 17:52 .bashrc
-rw-r--r--    1 user     user            17 Jun 14 17:52 .profile
-rwxr-xr-x    1 root     root           131 Jun 14 17:52 .user-entrypoint.sh
```

```bash
#!/bin/bash

nohup tail -f /home/user/flag.txt >/dev/null 2>&1 & #
disown

rm -f /home/user/flag.txt 2>&1 >/dev/null

bash -i
exit
```

Looking into the command `nohup` I [read](https://www.digitalocean.com/community/tutorials/nohup-command-in-linux):
> Nohup, short for no hang up is a command in Linux systems that keep processes running even after exiting the shell or terminal. Nohup prevents the processes or jobs from receiving the SIGHUP (Signal Hang UP) signal. This is a signal that is sent to a process upon closing or exiting the terminal. In this guide, we take a look at the nohup command and demonstrate how it can be used.

Ah ok, so this probably means that the tail process is still running, and since tail had flag.txt open before it was deleted, we can probably find it from its process.

```console
user@zombie:~$ ps
PID   USER     TIME   COMMAND
    1 root       0:00 /usr/sbin/sshd -D -e
    7 root       0:00 sshd: user [priv]
    9 user       0:00 sshd: user@pts/0
   10 user       0:00 {.user-entrypoin} /bin/bash /home/user/.user-entrypoint.sh
   11 user       0:00 tail -f /home/user/flag.txt
   13 user       0:00 bash -i
   20 user       0:00 ps
user@zombie:~$ ls /proc/11/fd
0  1  2  3
user@zombie:~$ cat /proc/11/fd/3
flag{6387e800943b0b468c2622ff858bf744}
```

## **Flag**: `flag{6387e800943b0b468c2622ff858bf744}`



