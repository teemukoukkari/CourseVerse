## Opetussovellus

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

Sovelluksen ominaisuuksia:
- [x] Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- [x] Opiskelija näkee listan kursseista ja voi liittyä kurssille.
- [x] Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
- [x] Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
- [ ] Opettaja pystyy luomaan uuden kurssin sekä muokkaamaan ja poistamaan kurssejaan
- [x] Opettaja pystyy lisäämään kurssisivulle tekstimateriaalia, monivalintatehtäviä ja automaattisesti tarkastettavia tekstivastauksia.
- [x] Opettaja pystyy vaihtamaan lisätyn materiaalin ja tehtävien järjestystä kurssisivulla
- [ ] Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

## Sovelluksen testaaminen
Sovellus on hostattuna osoitteessa [https://courseverse-w2hm.onrender.com/courses](https://courseverse-w2hm.onrender.com/courses). Kyseessä on ilmainen tilaus, joten on yleistä, että sivun ensimmäinen lataus voi kestää yli minuutin. Tämän jälkeen sivu toimii kuitenkin yleensä hyvin.

<details>
    <summary>Sovelluksen testaaminen (Docker)</summary>
    Mikäli olet käyttänyt Dockeria aikaisemmin ja se on asennettuna, tämä lienee vaivattomin tapa saada sovellus käyntiin omalla koneella.

    Kloonaa repo, siirry sen juurihakemistoon ja käynnistä sovellus  porttiin 8080 komennolla
    ```
    $ docker dompose up
    ```

    Huomaa, että postgres-tunnukset ja secret_key ovat selväkielisenä .yml-tiedostossa - tämä on toistaiseksi vain testaamista varten.
</details>

<details>
<summary>Sovelluksen testaaminen (Docker)/<summary>
## Sovelluksen testaaminen (perinteinen)
Vaihtoehtoisesti voit ottaa sovelluksen käyttöön kurssimateriaalissa esitetyllä tavalla. Edellytyksenä on, että postgres on asennettuna valmiiksi.

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:

```
DATABASE_URI=<tietokannen-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```

Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komnnoilla
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

Määritä vielä tietokannan skeema komennolla (varmista, että tietokanta on tyhjä ennen tätä)
```
$ psql < schema.sql
```

Nyt voit käynnistää sovelluksen komennolla
```
$ flask run
```
</details>