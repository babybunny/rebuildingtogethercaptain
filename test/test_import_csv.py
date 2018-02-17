import tempfile
import unittest
import app_engine_test_utils
import import_csv
from gae.room import ndb_models
from test import test_models


class TestImportCsv(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    test_models.CreateAll()

  def testImportSitesAndCaptains(self):

    # dump test data to a tmp files
    path_to_sites_data = tempfile.mktemp()
    with open(path_to_sites_data, 'wb') as io:
      io.write(TestImportCsv.SITES_DATA)
    path_to_captains_data = tempfile.mktemp()
    with open(path_to_captains_data, 'wb') as io:
      io.write(TestImportCsv.CAPTAINS_DATA)

    import_csv.import_sites(path_to_sites_data, 2442)
    import_csv.import_captains(path_to_captains_data)

    site = ndb_models.NewSite.query().filter(ndb_models.NewSite.number == "18010SAM").get()  # type: ndb_models.NewSite
    self.assertTrue(site)
    site_captains = list(site.sitecaptain_set)
    self.assertEqual(len(site_captains), 2)
    for site_captain in site_captains:
      ctype = site_captain.type
      captain = site_captain.captain.get()
      self.assertIn(ctype, ("Construction", "Volunteer"))
      if ctype == "Construction":
        self.assertEqual(captain.email, 'mike@nibbi.com')
      else:
        self.assertEqual(captain.email, 'bobn@nibbi.com')


  SITES_DATA = """\
Announcement Subject,Announcement Body,Site ID,Budgeted Cost in Campaign,Repair Application: Applicant's Name,Applicant Home Phone,Applicant Mobile Phone,Applicant Work Phone,Recipient's Street Address,Recipient's City,Recipient's Zip Code,Jurisdiction,Sponsor,Repair Application: RRP Test Results,Photos Link
subject of announcement,"announcement body, has some commas",18001DAL,"$10,000",Man Shu Lau,,(415) 350-7499,,221 South Hill Court,Daly City,94014,Daly City,Woodlawn Foundation & St. Andrews Church (volunteers),"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsksxU9or
subject of announcement,"announcement body, has some commas",18002SSF,"$5,250",Til Won,(650) 737-0378,,,102 Manzanita Ave,South San Francisco,94080,South San Francisco,First National Bank - CDBG South SF ,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmakxWNw
subject of announcement,"announcement body, has some commas",18003SSF,"$5,250",Kavita Sharma,(415) 774-6026,(415) 774-6025,,135 Arden Ave,South San Francisco,94080,South San Francisco,CDBG South SF - LDS Stanford (volunteers),Tested - Negative,https://flic.kr/s/aHsmdASNF9
subject of announcement,"announcement body, has some commas",18004SSF,"$3,250",Sunder Sujan,(650) 746-6302,(650) 580-9069,,229 Bonita Ave,South San Francisco,94080,South San Francisco,Nishkian Menninger - CDBG South SF ,Tested - Negative,https://flic.kr/s/aHsmcc2RiK
subject of announcement,"announcement body, has some commas",18005RWC,"$4,000",Mary Gail Lynch,(650) 366-8281,,,215 Oakdale St.,Redwood City,94062,Redwood City,Oracle - CDBG Redwood City ,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHskvEkfxS
subject of announcement,"announcement body, has some commas",18006RWC,"$4,000",Kimi Rosas,,(650) 833-9111,,639 Flynn Ave,Redwood City,94063,Redwood City,Whiting-Turner - CDBG Redwood City,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeLPcqP
subject of announcement,"announcement body, has some commas",18007RWC,"$4,000",Nancy Moore,(650) 369-6706,,,473 Ruby St.,Redwood City,94062,Redwood City,CDBG Redwood City,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmcc4Hdn
subject of announcement,"announcement body, has some commas",18008RWC,"$4,000",Hubert Bourland,(650) 365-7726,,,559 Oak Ridge Drive,Redwood City,94062,Redwood City,CDBG Redwood City,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHskvEmPBW
subject of announcement,"announcement body, has some commas",18009RWC,"$4,000",Maria Castillo,(650) 921-3831,(650) 771-1031,,3241 Hoover St,Redwood City,94063,Redwood City,CDBG Redwood City - Ebcon (volunteers),"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdAW5B1
subject of announcement,"announcement body, has some commas",18010SAM,,Katalina Ahoia,(650) 401-8147,,(650) 573-2056,624 Oceanview Avenue,San Mateo,94401,City of San Mateo,Nibbi Brothers Construction ,Tested - Negative,https://flic.kr/s/aHsmdAWAHo
subject of announcement,"announcement body, has some commas",18011SAM,"$3,000",Nadia McGraw,(650) 348-6707,(650) 346-3753,,1309 Huron Ave.,San Mateo,94401,City of San Mateo,CDBG San Mateo - Foster City Lions (volunteers),"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmcc6zbr
subject of announcement,"announcement body, has some commas",18012SAM,"$3,000",Frank Tu,(650) 345-3461,(650) 307-3121,,2145 Meadow View Place,San Mateo,94401,City of San Mateo,CDBG San Mateo - Crystal Springs Upland School (volunteers),Tested - Negative,https://flic.kr/s/aHsmdAXZFW
subject of announcement,"announcement body, has some commas",18013SAM,"$5,000",Lori Poultney,(650) 773-3034,(650) 773-3034,,1553 Monte Diablo Ave.,San Mateo,94401,City of San Mateo,BKF Engineers - CDBG  San Mateo,Tested - Positive,https://flic.kr/s/aHsmeLTyoT
subject of announcement,"announcement body, has some commas",18014SAM,"$15,000",Mary Kinney,(650) 343-1793,(650) 278-7610,(650) 265-5345,326 North Idaho Street,San Mateo,94401,City of San Mateo,Novo Construction & ABD Insurance - CDBG San Mateo,Tested - Negative,https://flic.kr/s/aHskBtPQhD
subject of announcement,"announcement body, has some commas",18015EPA,"$9,250",Atella Brackman,(650) 326-2160,,,2857 Temple Court,East Palo Alto,94303,San Mateo County,Siemens - CDBG San Mateo County,Tested - Negative,https://flic.kr/s/aHsmdB112w
subject of announcement,"announcement body, has some commas",18016EPA,"$4,250",Sharron Scoggins,(650) 323-1770,,,1523 Ursula Way,East Palo Alto,94303,San Mateo County,Woodside Priory - CDBG San Mateo County,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmcc9YXt
subject of announcement,"announcement body, has some commas",18017EPA,"$4,250",Thurman Smith,(650) 324-4341,(650) 888-7840,,256 Azalia Dr,East Palo Alto,94303,San Mateo County,TE Connectivity - CDBG San Mateo County,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmakF9Ss
subject of announcement,"announcement body, has some commas",18018EPA,"$4,250",Plocerfina Thompson,(650) 631-7671,(650) 631-7671,,107 Daphne Way,East Palo Alto,94303,San Mateo County,Wells Fargo - CDBG San Mateo County,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHskBtQW3e
subject of announcement,"announcement body, has some commas",18019EPA,"$4,250",Selbia Smith,(650) 322-7341,(650) 776-5922,,108 Verbena Dr.,East Palo Alto,94303,San Mateo County,Kiwanis Club of Menlo Park - CDBG San Mateo County,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeLVJKF
subject of announcement,"announcement body, has some commas",18020EPA,"$4,250",Leo Woodard,,(650) 518-0929 ,(650) 817-9070 ext 149,2250 Menalto Ave.,East Palo Alto,94303,San Mateo County,CDBG San Mateo County - Serra Fathers' Club (volunteers),"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeLWAR2
subject of announcement,"announcement body, has some commas",18021EPA,,Haitelenisia Mahe,(650) 600-2123,(650) 518-1374,,2260 Brentwood Ct,East Palo Alto,94303,San Mateo County,Nibbi Brothers Construction,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdB4ybW
subject of announcement,"announcement body, has some commas",18022MEN,"$4,250",Patricia Jacowsky,(650) 325-4752,(650) 291-9829,,832 15th Ave.,Menlo Park,94025,San Mateo County,Stanford Health Care - CDBG  San Mateo County,Tested - Positive,https://flic.kr/s/aHsmcceCVV
subject of announcement,"announcement body, has some commas",18023RWU,"$9,250",Roy Obana,(650) 257-7026,,,820 6th Avenue,Redwood City,94063,San Mateo County,"Trinity Episcopal, Christ Episcopal, First Presbyterian - CDBG SMC",Tested - Positive,
subject of announcement,"announcement body, has some commas",18024SUN,"$3,000",Lorraine Wolfington,(408) 735-8742,,,1070 Polk Ave,Sunnyvale,94086,Sunnyvale,Rambus,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHskvEuNby
subject of announcement,"announcement body, has some commas",18025SSF,"$7,000",South San Francisco Head Start Program (Site Contact: Yesenia Guzman),,,(650) 438-9036,825 Southwood Drive,South San Francisco,94080,South San Francisco,Genentech - CDBG SMC - SMC Dept of Education,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdB6M5Y
subject of announcement,"announcement body, has some commas",18026RWC,"$5,000",St. Francis Center (Site Contact: Dulce Pasillas),,,(650) 365-7829,780 Bradford Avenue,Redwood City,94086,Redwood City,W.L. Butler Construction - CDBG San Mateo County,Tested - Negative,https://flic.kr/s/aHskvEx36y
subject of announcement,"announcement body, has some commas",18027RWC,"$6,000",Redwood Church Preschool (Site Contact: Jennifer Corrales),,,(650) 562-7611,901 Madison Avenue,Redwood City,94061,Redwood City,Commercial Casework & Heritage Bank of Commerce - SMC Dept of Education,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeM2jVV
subject of announcement,"announcement body, has some commas",18028RWC,"$5,000",Samaritan House Free Clinic of RWC (Site Contact: Laura Bent),,,(650) 341-4081 ext 2020,114 5th Avenue,Redwood City,94063,Redwood City,Rotary Clubs Woodside/Portola Valley & Peninsula Sunrise - CDBG SMC,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHskBtWFbt
subject of announcement,"announcement body, has some commas",18029RWC,"$6,000",Garcia's Daycare (Site Contact: Maria Garcia),,,(650) 921-7673,278 Madrone Street,Redwood City,94061,Redwood City,Pentair - SMC Dept of Education,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeM4dMP
subject of announcement,"announcement body, has some commas",18030MEN,"$5,000",Haven Family House - Lifemoves (Site Contact: Jacob Stone),,,(650) 685-5880,260 Van Buren Rd.,Menlo Park,94025,San Mateo County,Cooley LLP - CDBG San Mateo County,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmakP61y
subject of announcement,"announcement body, has some commas",18031EPA,"$3,000",East Palo Alto Charter School (Site Contact: Eron Truran),,,(650) 614-9100,1286 Runnymede St.,East Palo Alto,94303,San Mateo County,WSGR Foundation - CDBG SMC,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdBchS3
subject of announcement,"announcement body, has some commas",18032EPA,"$5,000",Free at Last - (Site Contact: Sue Cortopassi),,,(650) 462-6992,1796 Bay Road,East Palo Alto,94303,San Mateo County,Trubeck Construction,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmcckd5F
subject of announcement,"announcement body, has some commas",18033SAM,"$5,000",Lisa's House - CORA's Emergency Shelter (Site Contact: Cheyrle Matteo),,,(650) 652-0800,,San Mateo,94403,City of San Mateo,Roche,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmeM7Xvi
subject of announcement,"announcement body, has some commas",18034SAM,"$5,000",Medina Family Daycare (Site Contact: Marcela Medina),,,(650) 445-5512,849 Patricia Ave.,San Mateo,94401,City of San Mateo,SMC Dept of Education - Notre Dame Fathers' Club (volunteers),"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsksyeCSn
subject of announcement,"announcement body, has some commas",18035MER,,Boys & Girls Club of Merced (Site Contact: Michael Pierick),,,(209) 722- 9922,615 W. 15th Street,Merced,95340,,Webcor Builders,n/a,https://flic.kr/s/aHskvECqf3
subject of announcement,"announcement body, has some commas",18036SAM,"$5,000",Rosemarie Aguiniga,,(650) 393-3147,,1029 East 5th Ave,San Mateo,94402,City of San Mateo,DES - CDBG San Mateo,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmckKt5z
subject of announcement,"announcement body, has some commas",18037EPA,"$3,000",East Palo Alto Charter School (Site Contact: Eron Truran),,,(650) 614-9100,1286 Runnymede St.,East Palo Alto,94303,San Mateo County,Kiwanis Club of Palo Alto & NCL Orchard Valley,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdBchS3
subject of announcement,"announcement body, has some commas",18038EPA,"$5,000",East Palo Alto Charter School (Site Contact: Eron Truran),,,(650) 614-9100,1286 Runnymede St.,East Palo Alto,94303,San Mateo County,Webcor Builders,"Not tested - Not required to test, assume no lead",https://flic.kr/s/aHsmdBchS3"""

  CAPTAINS_DATA = """\
Site ID,Name,ROOMS Captain ID,Phone,Email,Project Role
18001DAL,John Solano,R00438,(650) 678-6109,john@johnsolanoconstruction.com,Construction Captain
18001DAL,Lisa Angelot,R00238,(650) 455-3555,lange16093@aol.com,Volunteer Captain
18002SSF,Bill Provence,R00029,(650) 355-1729,billprovence@yahoo.com,Construction Captain
18002SSF,Bill Tecson,R00031,(650) 875-4860,btecson@familybank.com,Volunteer Captain
18003SSF,Jim Benson,R00169,(650) 544-4653,jb11hmb@gmail.com,Construction Captain
18003SSF,Laura Pearson,R00448,,laurapear@gmail.com,Volunteer Captain
18004SSF,Dan Goodman,R00079,(650) 714-6312,danmgoodman@gmail.com,Construction Captain
18004SSF,Julie Hagelshaw,R00422,(415) 541-9477,jhagelshaw@nishkian.com,Volunteer Captain
18005RWC,Kim Nguyen,R00432,(650) 204-0986,kimn_1@yahoo.com,Volunteer Captain
18005RWC,Matt Sorgenfrei,R00257,(650) 704-6806,sorgenfrei.matt@gmail.com,Construction Captain
18006RWC,Jacob LaMontagne,R00444,(240) 372-2908,jacob.lamontagne@whiting-turner.com,Volunteer Captain
18006RWC,Tom Wooden,R00384,(925) 580-5207,thomas.wooden@whiting-turner.com,Construction Captain
18007RWC,Don Kirk,R00400,(650) 924-5279,don@donkirk.com,Construction Captain
18009RWC,Erik Bergstrom,R00435,(650) 773-1272,ebcon.corp@gmail.com,Construction Captain
"18010SAM, 18021EPA",Michael Nibbi,R00269,(415) 412-7168,mike@nibbi.com,Construction Captain
"18010SAM, 18021EPA",Robert Nibbi,R00331,(415) 863-1820,bobn@nibbi.com,Volunteer Captain
18011SAM,Ray Rosenthal,R00308,(650) 465-7158,rosieinc45@gmail.com,Construction Captain
18012SAM,Bill Kwong,R00026,(650) 342-4175,bkwong@crystal.csus.org,Volunteer Captain
18012SAM,Chi-hwa Shao,R00057,(650) 222-5467,shaochihwa@gmail.com,Construction Captain
18012SAM,Vivian Shao,R00443,(650) 347-8848,vshao@csus.org,Volunteer Captain
18013SAM,Alex Cabezon,R00003,(650) 482-6350,acabezon@bkf.com,Volunteer Captain
18013SAM,Craig Wallace,R00070,(650) 533-8850,craig.wallace@yahoo.com,Construction Captain
18014SAM,Andrew Duvall,R00442,(415) 542-6320,aduvall@novoconstruction.com,Construction Captain
18015EPA,Don Van Creveld,R00102,(925) 330-6194,misterrefurb@gmail.com,Construction Captain
18015EPA,Josh Martin,R00193,(650) 933-8176,josh.martin@siemens.com,Volunteer Captain
18016EPA,Lawrence Hu,R00230,(650) 450-0959,lhu_ccas@yahoo.com,Construction Captain
18016EPA,Tim Molak,R00378,(650) 851-6117,tmolak@prioryca.org,Volunteer Captain
18017EPA,John Sheckleton,R00445,,jsheckleton@te.com,Volunteer Captain
18017EPA,Robert Pereira,R00333,(408) 813-0684,rjpereira2001@gmail.com,Construction Captain
18018EPA,Bob Rosenberg,R00035,(650) 465-0344,bob@gr8work.com,Construction Captain
18018EPA,Linda Guzman,R00446,(650) 400-5659,linda.m.guzman@wellsfargo.com,Volunteer Captain
18019EPA,Thompson Sako,R00376,(415) 990-3903,tsako@pacbell.net,Construction Captain
18019EPA,Tom Boeddiker,R00381,(650) 614-3500,tboeddiker@gmail.com,Volunteer Captain
18020EPA,Jeff Jerome,R00403,(650) 596-6160,jeffriejerome@yahoo.com,Construction Captain
18022MEN,Brooks Posegate,R00045,(650) 367-5977,brooks.posegate@hotmail.com,Construction Captain
18022MEN,Tessa Wei,R00440,(415) 254-9250,twei@stanfordhealthcare.org,Volunteer Captain
18023RWU,Andy Ritger,R00009,(408) 667-6038,andy.ritger@gmail.com,Construction Captain
18023RWU,John Crevelt,R00177,(650) 743-0611,krefeldsawards@gmail.com,Construction Captain
18023RWU,John Tastor,R00439,(415) 298-4611,johntastor85@gmail.com,Volunteer Captain
18025SSF,Edna Stoehr,R00109,(650) 477-8563,edna@gene.com,Volunteer Captain
18025SSF,Gitte Jensen,R00137,(650) 438-2340,jensen.gitte@gene.com,Volunteer Captain
18025SSF,Peter Yribar,R00300,(650) 255-4085,yribar.peter@gene.com,Construction Captain
18026RWC,Joel Butler,R00175,(650) 743-8018,joel.butler@wlbutler.com,Construction Captain
18027RWC,Edward Greilich,R00110,(510) 813-4400,eg@commercialcasework.com,Construction Captain
18027RWC,Toby Cordone,R00379,(408) 494-4528,toby.cordone@herbank.com,Volunteer Captain
18028RWC,David Kirk,R00442,(650) 384-5758,dgkirk@gmail.com,Construction Captain
18028RWC,Ken Hayes,R00213,(650) 365-0600 x15,khayes@thehayesgroup.com,Volunteer Captain
18028RWC,Russ Castle,R00441,(650) 722-3974,russ@insurancebycastle.com,Volunteer Captain
18029RWC,Frances Larios,R00434,,frances.larios@pentair.com,Volunteer Captain
18029RWC,Spence Leslie,R00357,(650) 474-7414,spencerkleslie@gmail.com,Construction Captain
18030MEN,Michael Tenta,R00270,(650) 843-5636,mtenta@cooley.com,Volunteer Captain
18030MEN,Pete Hooper,R00299,(650) 303-2156,hooperpete@gmail.com,Construction Captain
18038EPA,Brian Dahlquist,R00040,(650) 787-4885,brian.dahlquist@efi.com,Construction Captain
18038EPA,Candace Demele,R00447,(650) 793-5699,cdemele@rocketmail.com,Volunteer Captain
18031EPA,Gail McFall,R00129,(650) 461-6626,gail.mcfall@gmail.com,Volunteer Captain
18031EPA,Jim McFall,R00172,(650) 380-8544,wjmcfall@gmail.com,Construction Captain
18038EPA,Marty Deggeller,R00254,(650) 321-1029,martydeg@pacbell.net,Volunteer Captain
18032EPA,Amanda Carson,R00402,(650) 636-6727,amanda.carson@gmail.com,Volunteer Captain
18032EPA,Carlos Delgadillo,R00418,,carlos.delgadillo@truebeck.com,Construction Captain
18033SAM,Kevin Marks,R00221,(650) 283-9151,kevamarks@gmail.com,Construction Captain
18034SAM,Kenneth Hines,R00215,(650) 823-8355,ken.r.hines@gmail.com,Construction Captain
18034SAM,Ron Strong,R00449,,strongra@gmail.com,Volunteer Captain
18036SAM,Kevin Norman,R00406,(650) 364-6453 x 253,knorman@des-ae.com,Construction Captain
18036SAM,Mohammed Sedqi,R00122,(650) 364-6453 ,msedqi@des-ae.com,Volunteer Captain\
"""