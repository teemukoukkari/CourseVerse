## Opetussovellus

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

Sovelluksen ominaisuuksia:
- [x] Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- [x] Opiskelija näkee listan kursseista ja voi liittyä kurssille.
- [x] Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
- [x] Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
- [x] Opettaja pystyy luomaan uuden kurssin sekä muokkaamaan ja poistamaan kurssejaan
- [x] Opettaja pystyy lisäämään kurssisivulle tekstimateriaalia, monivalintatehtäviä ja automaattisesti tarkastettavia tekstivastauksia.
- [x] Opettaja pystyy vaihtamaan lisätyn materiaalin ja tehtävien järjestystä kurssisivulla
- [x] Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

## Sovelluksen testaaminen verkossa
Sovellus on hostattuna osoitteessa [https://courseverse-w2hm.onrender.com/courses](https://courseverse-w2hm.onrender.com/courses). Siellä on myös esimerkkikurssi valmiiksi. Kyseessä on ilmainen tilaus, joten on yleistä, että sivun ensimmäinen lataus voi kestää yli minuutin. Tämän jälkeen sivu toimii kuitenkin yleensä hyvin.

## Sovelluksen testaaminen omalla koneella
Vaihtoehtoisesti voit ottaa sovelluksen käyttöön kurssimateriaalissa esitetyllä tavalla. Edellytyksenä on, että postgres on asennettuna valmiiksi.

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurihakemistoon.

Luo aluksi Postgresiin tietokanta sovellusta varten. Esimerkiksi:
```
$ psql
user=# CREATE DATABASE courseverse;
```

Tämän jälkeen määritä tietokannan skeema:
```
$ psql -d courseverse < schema.sql
```

Luo projektin juurihakemistoon .env-tiedosto, jonka sisältö on esimerkiksi seuraava:
```
DATABASE_URI=postgresql:///courseverse
SECRET_KEY=<salainen-avain>
```

Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

Nyt voit käynnistää sovelluksen komennolla
```
$ flask run
```