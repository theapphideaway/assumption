# Text credits

Attribution required by the licences of the texts bundled in this app. Mirror
this on an in-app credits screen before release.

## Scripture

**World English Bible** — public domain, copyright waived by the publisher.
Source: <https://github.com/TehShrike/world-english-bible>

**Russian Synodal Translation (Синодальный перевод, 1876)** — public domain.
Source: <https://github.com/seven1m/open-bibles>

**Greek New Testament, Patriarchal Text of 1904** — Dr. Maurice A. Robinson's
edition of Antoniades' 1904/1912 Patriarchal text. Public domain.
Source: <https://github.com/byztxt/greektext-antoniades>

**Swete's Septuagint** — *The Old Testament in Greek According to the
Septuagint*, ed. Henry Barclay Swete. The text is public domain by age. The
digitisation is by the Open Greek and Latin Project's First1KGreek and is
licensed **CC BY-SA 4.0**, which obliges us to credit it and to keep the text
itself under the same licence.

> Swete's Septuagint, digitised by the Open Greek and Latin Project
> (First1KGreek), used under CC BY-SA 4.0.
> <https://github.com/OpenGreekAndLatin/First1KGreek>
> via <https://github.com/nathans/lxx-swete>

CC BY-SA binds the *text*, not this application's own code, so it does not
force the app open-source. It does mean the Greek Old Testament must stay
attributed and redistributable under the same terms.

**Church Slavonic Psalter (Елизаветинская Библия, 1751)** — taken from the
Ponomar liturgics suite, `Ponomar/languages/cu/bible/elis/Psalm.text`.
Source: <https://github.com/typiconman/ponomar>

> **OPEN LICENSING QUESTION — resolve before public release.**
> The Ponomar *repository* is licensed GPL v3. The Elizabeth Bible itself dates
> from 1751 and is public domain by age, and a licence cannot encumber a work
> its holder does not own — so the GPL most likely covers Ponomar's software
> suite rather than the scripture files that sit in the same tree. That is a
> reasonable reading, not a confirmed one.
>
> The Slavonic Computing Initiative (sci.ponomar.net) has been asked to confirm
> whether the GPL extends to the text files under `Ponomar/languages/`. Record
> their answer here when it arrives.
>
> If they say the text IS GPL-covered, replace it: GPL and App Store
> distribution conflict, and the parish should not be distributing anything in
> violation. `manage.py load_scripture <file> --edition elizabeth` makes the
> swap a single command, and only the Psalter is used.

## Lectionary

**Daily readings** — imported from the calendarium fixture of **orthocal**, by
Brian Glass, used under the **MIT Licence**. Common and Greek-tradition rows
are kept; Slavic rows are dropped, Assumption being GOARCH.
Source: <https://github.com/brianglass/orthocal-python>

> MIT License. Copyright (c) Brian Glass. Permission is hereby granted, free of
> charge, to any person obtaining a copy of this software and associated
> documentation files, to deal in the Software without restriction. The above
> copyright notice and this permission notice shall be included in all copies
> or substantial portions of the Software.

MIT imposes no copyleft, so this carries none of the concerns attached to the
Church Slavonic psalter above.

## Prayers

Traditional received English, Greek and Church Slavonic, in the forms in
common liturgical use and long out of copyright. Not transcribed from any
modern published prayer book — those translations are under copyright.
