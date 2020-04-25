import tempfile
import unittest
import textwrap
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

    import_csv.import_sites(path_to_sites_data)
    import_csv.import_captains(path_to_captains_data)

    site = ndb_models.NewSite.query().filter(ndb_models.NewSite.number == "50010SAM").get()  # type: ndb_models.NewSite
    self.assertTrue(site)
    site_captains = list(site.sitecaptain_set)
    self.assertEqual(len(site_captains), 2)
    for site_captain in site_captains:
      ctype = site_captain.type
      captain = site_captain.captain.get()
      self.assertIn(ctype, ("Construction", "Volunteer"))
      if ctype == "Construction":
        self.assertEqual(captain.email, 'metropolitan@boulevard.com')
      else:
        self.assertEqual(captain.email, 'aristocratic@theorist.com')


  SITES_DATA = textwrap.dedent("""\
    Announcement Subject,Announcement Body,Site ID,Budget,Homeowner/Site Contact Name,Applicant Phone,Applicant Mobile Phone,Street Address,City,Zipcode,Jurisdiction,Sponsor Name,Program Year,CDBG Funding Source
    subject,"announcement body, which has some commas",50001DAL,$1007,Malay Nothing,9999999999,(608) 123-4567,123 Champaign St,"Row, Rectilinear",00000,Argue Wendy,Pompon,2050
    subject,"announcement body, which has some commas",50002SSF,"$1,007.00",Efficacious Gizzard,9999999999,(608) 123-4567,123 Radii St,"Bronchi, Epsom",00000,Curie Thousand,Sibling,2050
    subject,"announcement body, which has some commas",50003SSF,$1007,Enthusiast Baffin,9999999999,(608) 123-4567,123 Expositor St,"Placeable, Knives",00000,Egret Fume,Indirect,2050
    subject,"announcement body, which has some commas",50004SSF,$1007,Nordstrom Brindisi,9999999999,(608) 123-4567,123 Dennis St,"Wavy, Lookout",00000,Airy Rib,Magnetic,2050
    subject,"announcement body, which has some commas",50005RWC,$1007,Incorrigible Isochronal,9999999999,(608) 123-4567,123 Gerbil St,"Systemwide, Ergative",00000,Soundproof Orthodontic,Leguminous,2050
    subject,"announcement body, which has some commas",50006RWC,$1007,Paraxial Blackbody,9999999999,(608) 123-4567,123 Glory St,"Worrisome, Valeur",00000,Slapdash Shipbuild,Heidegger,2050
    subject,"announcement body, which has some commas",50007RWC,$1007,Dialectic Alger,9999999999,(608) 123-4567,123 Derivate St,"Utter, Fusion",00000,Politico Shore,Missionary,2050
    subject,"announcement body, which has some commas",50008RWC,$1007,Premonition Gasp,9999999999,(608) 123-4567,123 Wove St,"Culvert, Holman",00000,Algiers Trifluoride,Midsection,2050
    subject,"announcement body, which has some commas",50009RWC,$1007,Embryology Dill,9999999999,(608) 123-4567,123 Quartz St,"Oklahoma, Tyrannicide",00000,Dew Chateau,Alkali,2050
    subject,"announcement body, which has some commas",50010SAM,$1007,Phobic Calibrate,9999999999,(608) 123-4567,123 Moorish St,"Hagiography, Saud",00000,Empathic Lehigh,Fishy,2050
    subject,"announcement body, which has some commas",50011SAM,$1007,Calculate Disastrous,9999999999,(608) 123-4567,123 Shod St,"Commissariat, Equinoctial",00000,Tananarive Nomadic,Trigram,2050
    subject,"announcement body, which has some commas",50012SAM,$1007,Me Spoke,9999999999,(608) 123-4567,123 Cern St,"Adrift, Tasteful",00000,Bitterroot Nashua,Premiere,2050
    subject,"announcement body, which has some commas",50013SAM,$1007,Byzantine Officio,9999999999,(608) 123-4567,123 Scatterbrain St,"Organ, Regulatory",00000,Levulose Diffusive,Denudation,2050
    subject,"announcement body, which has some commas",50014SAM,$1007,Philip Committable,9999999999,(608) 123-4567,123 Interpolatory St,"Cornflower, Sockeye",00000,Blockage Waste,Nought,2050
    subject,"announcement body, which has some commas",50015EPA,$1007,Devolve Hillmen,9999999999,(608) 123-4567,123 Pelican St,"Slovenia, Patriarch",00000,Moderate Caroline,Gnomonic,2050
    subject,"announcement body, which has some commas",50016EPA,$1007,Sightsee Anomie,9999999999,(608) 123-4567,123 Dross St,"Crept, Pap",00000,Hid Armstrong,Matrilineal,2050
    subject,"announcement body, which has some commas",50017EPA,$1007,Import Counterproductive,9999999999,(608) 123-4567,123 Sagittarius St,"Kruger, Mackerel",00000,Otherwise Alvin,Suez,2050
    subject,"announcement body, which has some commas",50018EPA,$1007,Serology Harmonious,9999999999,(608) 123-4567,123 Noodle St,"Camellia, Galloway",00000,Transferring Amphibole,Nevertheless,2050
    subject,"announcement body, which has some commas",50019EPA,$1007,Whitish Callus,9999999999,(608) 123-4567,123 Damocles St,"Immediate, Trencherman",00000,Luminosity Tactic,Briton,2050
    subject,"announcement body, which has some commas",50020EPA,$1007,Alice Vendor,9999999999,(608) 123-4567,123 Inconvenient St,"Hard, Anorthic",00000,Bimetallism Ames,Fairy,2050
    subject,"announcement body, which has some commas",50021EPA,$1007,Stony Monolith,9999999999,(608) 123-4567,123 Matins St,"Spec, Exegesis",00000,Picnicking Equanimity,Millenarian,2050
    subject,"announcement body, which has some commas",50022MEN,$1007,Haney Buccaneer,9999999999,(608) 123-4567,123 Antenna St,"Aborning, Batavia",00000,Heterogeneity Damascus,Auto,2050
    subject,"announcement body, which has some commas",50023RWU,$1007,Jam Ojibwa,9999999999,(608) 123-4567,123 Jacobite St,"Comprehensive, Dud",00000,Gift Doe,Sorghum,2050
    subject,"announcement body, which has some commas",50024SUN,$1007,Eden Liable,9999999999,(608) 123-4567,123 Quitter St,"Matriarchy, Accumulate",00000,Forfeiture Millionth,Reilly,2050
    subject,"announcement body, which has some commas",50025SSF,$1007,Woodcock Inactivate,9999999999,(608) 123-4567,123 Genera St,"Mesozoic, Concatenate",00000,Funeral Immaterial,Treasonous,2050
    subject,"announcement body, which has some commas",50026RWC,$1007,Finger Awesome,9999999999,(608) 123-4567,123 Canine St,"Honoraria, Whee",00000,Prussic Vortices,Genesco,2050
    subject,"announcement body, which has some commas",50027RWC,$1007,Segundo Need,9999999999,(608) 123-4567,123 Reprise St,"Droplet, Conjuncture",00000,Witchcraft Gar,Abramson,2050
    subject,"announcement body, which has some commas",50028RWC,$1007,Rotate Exorcism,9999999999,(608) 123-4567,123 Kowalski St,"Depression, Dahomey",00000,Banquet Dailey,Chit,2050
    subject,"announcement body, which has some commas",50029RWC,$1007,Chimney Shrapnel,9999999999,(608) 123-4567,123 Recalcitrant St,"Citizen, Adulate",00000,Cardinal Inability,Ironwood,2050
    subject,"announcement body, which has some commas",50030MEN,$1007,Giraffe Beluga,9999999999,(608) 123-4567,123 Sproul St,"Vodka, Hog",00000,Tantalum Grow,Salvage,2050
    subject,"announcement body, which has some commas",50031EPA,$1007,Accident Melamine,9999999999,(608) 123-4567,123 Ellipsometer St,"Impractical, Quadrangular",00000,Semiramis Convivial,Daedalus,2050
    subject,"announcement body, which has some commas",50032EPA,$1007,Crunchy Crandall,9999999999,(608) 123-4567,123 Mushroom St,"Blitz, Daddy",00000,Chinamen Alder,Beckon,2050
    subject,"announcement body, which has some commas",50033SAM,$1007,Aboard Lucy,9999999999,(608) 123-4567,123 Prestidigitate St,"Jehovah, Grub",00000,Doctrine Albrecht,Delilah,2050
    subject,"announcement body, which has some commas",50034SAM,$1007,Past Ian,9999999999,(608) 123-4567,123 Flea St,"Parentheses, Future",00000,Arclength Crete,Camelot,2050
    subject,"announcement body, which has some commas",50035MER,$1007,Catalpa Matrimony,9999999999,(608) 123-4567,123 Conferring St,"Operable, Coprocessor",00000,Attention Yates,Yosemite,2050
    subject,"announcement body, which has some commas",50036SAM,$1007,Mcmullen Invitation,9999999999,(608) 123-4567,123 Stonehenge St,"Kikuyu, Sum",00000,Nuance Onlooking,Thrash,2050
    subject,"announcement body, which has some commas",50037EPA,$1007,Automorphism Lisbon,9999999999,(608) 123-4567,123 Onrushing St,"Otiose, Soggy",00000,Portraiture Siltstone,Godwin,2050
    subject,"announcement body, which has some commas",50038EPA,$1007,Pbs Pecuniary,9999999999,(608) 123-4567,123 Teleology St,"Lear, Latinate",00000,Glide Pilewort,Burial,2050\
    """)

  CAPTAINS_DATA = textwrap.dedent("""\
    Site ID,Name,ROOMS Captain ID,Phone,Email,Captain Type
    50001DAL,Assimilate Pacemake,R00438,608) 123-4567,flutter@telescope.com,Construction Captain
    50001DAL,Solidarity Countdown,R00238,608) 123-4567,neptune@flan.com,Volunteer Captain
    50002SSF,Paul Peppergrass,R00029,608) 123-4567,told@quadrivium.com,Construction Captain
    50002SSF,Liberate Ocarina,R00031,608) 123-4567,timetable@sultan.com,Volunteer Captain
    50003SSF,Angle Bartender,R00169,608) 123-4567,barberry@printout.com,Construction Captain
    50003SSF,General Arden,R00448,608) 123-4567,metalwork@plod.com,Volunteer Captain
    50004SSF,Companionway Encryption,R00079,608) 123-4567,sepoy@three.com,Construction Captain
    50004SSF,Berry Perjury,R00422,608) 123-4567,broody@dendritic.com,Volunteer Captain
    50005RWC,Magnificent Novak,R00432,608) 123-4567,lutetium@luggage.com,Volunteer Captain
    50005RWC,Chromosphere Tuberous,R00257,608) 123-4567,bleach@nocturne.com,Construction Captain
    50006RWC,Sang Taffy,R00444,608) 123-4567,violate@coeducation.com,Volunteer Captain
    50006RWC,Licensable Artifact,R00384,608) 123-4567,rehearsal@karate.com,Construction Captain
    50007RWC,Coffey Friar,R00400,608) 123-4567,permeate@incite.com,Construction Captain
    50009RWC,Sardine Nit,R00435,608) 123-4567,skiff@aircraft.com,Construction Captain
    "50010SAM, 50021EPA",Anthony Pinkie,R00269,608) 123-4567,metropolitan@boulevard.com,Construction Captain
    "50010SAM, 50021EPA",Chat Dull,R00331,608) 123-4567,aristocratic@theorist.com,Volunteer Captain
    50011SAM,Archae Falsify,R00308,608) 123-4567,mandatory@myriad.com,Construction Captain
    50012SAM,Ontogeny Shine,R00026,608) 123-4567,deputation@stratagem.com,Volunteer Captain
    50012SAM,Avow Manhattan,R00057,608) 123-4567,public@clubroom.com,Construction Captain
    50012SAM,Adequacy Software,R00443,608) 123-4567,permitted@blanch.com,Volunteer Captain
    50013SAM,Salient Deadhead,R00003,608) 123-4567,scandium@washbasin.com,Volunteer Captain
    50013SAM,Georgia Sleight,R00070,608) 123-4567,birdseed@nature.com,Construction Captain
    50014SAM,Promulgate Christiana,R00442,608) 123-4567,oocyte@obstruct.com,Construction Captain
    50015EPA,Danube Smash,R00102,608) 123-4567,tugboat@resplendent.com,Construction Captain
    50015EPA,Main Sudden,R00193,608) 123-4567,vintner@sommelier.com,Volunteer Captain
    50016EPA,Lacrosse Format,R00230,608) 123-4567,potatoes@aluminate.com,Construction Captain
    50016EPA,Halide Loy,R00378,608) 123-4567,lavender@chandler.com,Volunteer Captain
    50017EPA,Rumford Antithetic,R00445,608) 123-4567,agnew@together.com,Volunteer Captain
    50017EPA,Wander Glitch,R00333,608) 123-4567,bronx@bolo.com,Construction Captain
    50018EPA,Brandon Truly,R00035,608) 123-4567,bali@pidgin.com,Construction Captain
    50018EPA,Winthrop Cable,R00446,608) 123-4567,navajo@neurosis.com,Volunteer Captain
    50019EPA,Impressive I'll,R00376,608) 123-4567,freshwater@ripoff.com,Construction Captain
    50019EPA,Sanhedrin Mythology,R00381,608) 123-4567,mutual@slipshod.com,Volunteer Captain
    50020EPA,Gait Diabetic,R00403,608) 123-4567,flop@infatuate.com,Construction Captain
    50022MEN,Thyme Terrific,R00045,608) 123-4567,dextrous@carnal.com,Construction Captain
    50022MEN,Newcastle Dialysis,R00440,608) 123-4567,boston@platinum.com,Volunteer Captain
    50023RWU,Communicable Coachmen,R00009,608) 123-4567,tsar@virgin.com,Construction Captain
    50023RWU,Savonarola Inexorable,R00177,608) 123-4567,rancorous@plenty.com,Construction Captain
    50023RWU,Minstrelsy Allocate,R00439,608) 123-4567,inviolate@farkas.com,Volunteer Captain
    50025SSF,Clint Malnourished,R00109,608) 123-4567,inert@breeze.com,Volunteer Captain
    50025SSF,Aphelion Hurdle,R00137,608) 123-4567,kola@polymeric.com,Volunteer Captain
    50025SSF,Internal Julio,R00300,608) 123-4567,calculable@abet.com,Construction Captain
    50026RWC,Premonition Millionfold,R00175,608) 123-4567,vase@pushpin.com,Construction Captain
    50027RWC,First Upsurge,R00110,608) 123-4567,skyward@refractory.com,Construction Captain
    50027RWC,Illumine Ernest,R00379,608) 123-4567,assist@canterbury.com,Volunteer Captain
    50028RWC,Cosy Ursula,R00442,608) 123-4567,siren@rubble.com,Construction Captain
    50028RWC,Complex Hearken,R00213,608) 123-4567,eastward@decertify.com,Volunteer Captain
    50028RWC,Lucifer Pest,R00441,608) 123-4567,ironic@cranny.com,Volunteer Captain
    50029RWC,Judo Homogeneity,R00434,608) 123-4567,let@oviduct.com,Volunteer Captain
    50029RWC,Extension Sworn,R00357,608) 123-4567,swelter@woodwind.com,Construction Captain
    50030MEN,Digress Seasonal,R00270,608) 123-4567,silty@transmittal.com,Volunteer Captain
    50030MEN,Angela Godhead,R00299,608) 123-4567,chorale@entropy.com,Construction Captain
    50038EPA,Westfield Boson,R00040,608) 123-4567,litany@onondaga.com,Construction Captain
    50038EPA,Coffee Seductive,R00447,608) 123-4567,pious@stacy.com,Volunteer Captain
    50031EPA,Ode Baudelaire,R00129,608) 123-4567,concern@alasdair.com,Volunteer Captain
    50031EPA,Sabra Mutandis,R00172,608) 123-4567,patois@madcap.com,Construction Captain
    50038EPA,Slake Herkimer,R00254,608) 123-4567,wack@wrapup.com,Volunteer Captain
    50032EPA,Prexy Complicity,R00402,608) 123-4567,waterhouse@typhon.com,Volunteer Captain
    50032EPA,Grata Berate,R00418,608) 123-4567,tent@strike.com,Construction Captain
    50033SAM,Fibrin Polopony,R00221,608) 123-4567,hartford@douce.com,Construction Captain
    50034SAM,Theoretician Votive,R00215,608) 123-4567,georgetown@schoolhouse.com,Construction Captain
    50034SAM,Gentle Davis,R00449,608) 123-4567,penguin@shish.com,Volunteer Captain
    50036SAM,Silicate Lanky,R00406,608) 123-4567,sacrilege@hijack.com,Construction Captain
    50036SAM,Muzo Videotape,R00122,608) 123-4567,gait@giles.com,Volunteer Captain
    """)
