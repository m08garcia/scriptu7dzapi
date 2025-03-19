import csv
import os
import subprocess
import datetime
import re
import sys
import requests
import json
import io

# URL del script en Vercel
VERCEL_SCRIPT_URL = "https://scriptu7dzapi.vercel.app/script.py"

# ========== DATOS DE CANALES INTEGRADOS ==========
CSV_CONTENT = """Lista canales ZAPI 16-03-2025
La 1;http://ott.zapitv.com/live/eds_c2/la1_4k/dash_live_enc/la1_4k.mpd?begin={utc}&end={utcend};a3abc44525eef3b0a7af9138a9dbe34a:7740f8ae4223ce5ba293028f7f78f1c1
LA 2;https://ott.zapitv.com/live/eds_c2/la_2/dash_live_enc/la_2.mpd?begin={utc}&end={utcend};ecd7ee75e0e88f267ace6bd7d9d70d83:eb196d2b2dc28418f465532c5d1182c0
ANTENA 3;https://ott.zapitv.com/live/eds_c2/antena_3/dash_live_enc/antena_3.mpd?begin={utc}&end={utcend};8a9e74b80c7cefa177926fc90eb05988:54e2cb64384e73b37b19d8c50e9479a4
CUATRO;https://ott.zapitv.com/live/eds_c2/cuatro/dash_live_enc/cuatro.mpd?begin={utc}&end={utcend};257fafffad77ccb5b8224d8fac6c9d62:81ebfc96640b0c8446c232f198b97dec
TELECINCO;https://ott.zapitv.com/live/eds_c2/telecinco/dash_live_enc/telecinco.mpd?begin={utc}&end={utcend};6e1dbacf4b932a11cd6cecb741def23d:0375536d6e512003972d1d6ea1f4d7c0
LA SEXTA;https://ott.zapitv.com/live/eds_c2/la_sexta/dash_live_enc/la_sexta.mpd?begin={utc}&end={utcend};239e5526ecb62d7b41c97641ea486549:93bfa21ee2211c271b7f0e1944a87818
CLAN TVE;https://ott.zapitv.com/live/eds_c2/clan_tv_hd/dash_live_enc/clan_tv_hd.mpd?begin={utc}&end={utcend};5daeec78aaec0ebb3353c5f7ebd16690:a56bd13e0cde801bb05c668b7578dfad
NICKELODEON;https://ott.zapitv.com/live/eds_c2/nickelodeon/dash_live_enc/nickelodeon.mpd?begin={utc}&end={utcend};eb21df65b1aae6fe7fe71cef1a7c79f6:e412464631ed10382d07b4467acdff19
NICK JR;https://ott.zapitv.com/live/eds_c2/nick_jr/dash_live_enc/nick_jr.mpd?begin={utc}&end={utcend};9288b676a6758b2f90b6b38f4b47f122:9f777abf518d699f4f5992dd9db8b1fa
BOING;https://ott.zapitv.com/live/eds_c2/boing/dash_live_enc/boing.mpd?begin={utc}&end={utcend};97c3e5f52bf51efe706c221930bc2b5b:b9473af4e52eaa9c9def9f8a5c54333c
ENFAMILIA;https://ott.zapitv.com/live/eds_c2/enfamilia/dash_live_enc/enfamilia.mpd?begin={utc}&end={utcend};aa360c3c1de766745176da004f574f25:1b2fd687dd8cb38132cab84a1342f02d
HOLLYWOOD;https://ott.zapitv.com/live/eds_c2/hollywood_hd/dash_live_enc/hollywood_hd.mpd?begin={utc}&end={utcend};38b0a87ba1614db52f1520191282a0db:af101261419cdcf7c09b82592eac862a
AMC;https://ott.zapitv.com/live/eds_c2/amc_hd/dash_live_enc/amc_hd.mpd?begin={utc}&end={utcend};ffec3dec40cb61a45e969c84977615ef:c6fbbe1e506a4323d3046b30731c9d52
TCM;https://ott.zapitv.com/live/eds_c2/tcm_moderno/dash_live_enc/tcm_moderno.mpd?begin={utc}&end={utcend};1ac0887faa9a185c93a2b989bff2e24b:22831d8c2d1133edf6b8db84087b5854
XTRM;https://ott.zapitv.com/live/eds_c2/xtrm_hd/dash_live_enc/xtrm_hd.mpd?begin={utc}&end={utcend};563e6e1367e0c8c0f6643cf0ae92c4e7:7a84ece91b690c5b717eeffd58a55b04
SOMOS;https://ott.zapitv.com/live/eds_c2/somos/dash_live_enc/somos.mpd?begin={utc}&end={utcend};8a8727d4973b18f61b29ac751b8a7522:10a11fe6ef837a5851cc6eeea7c08dc2
SYFY;https://ott.zapitv.com/live/eds_c2/syfy/dash_live_enc/syfy.mpd?begin={utc}&end={utcend};95ec1e26e80c38258a30101d06c8cbf7:0d0df5189256c0bf32c0cd0976bac5bd
ESCAPA;https://ott.zapitv.com/live/eds_c2/escapatv/dash_live_enc/escapatv.mpd?begin={utc}&end={utcend};1db8d673907b855cc52fa6c030aae18a:119e1f5bfe90e95d9b049cbf7dc66e45
WARNERTV;https://ott.zapitv.com/live/eds_c2/tnt/dash_live_enc/tnt.mpd?begin={utc}&end={utcend};33947fe5bd6af392efd09f7431e1fa54:02cef33e07cb49b26b0e099ba7467e97
AXN;https://ott.zapitv.com/live/eds_c2/axn/dash_live_enc/axn.mpd?begin={utc}&end={utcend};17b4b5cdbb271e7f6d97e38a04a2d27f:75aef15c20e7a17c64b71d2f840a6f5d
AXN MOVIES;https://ott.zapitv.com/live/eds_c2/axn_white/dash_live_enc/axn_white.mpd?begin={utc}&end={utcend};f9e4be09926c262effa2b5381ae3553d:d630e04e0c5e3f98dc38840be1c1dd4c
CALLE 13;https://ott.zapitv.com/live/eds_c2/calle_13/dash_live_enc/calle_13.mpd?begin={utc}&end={utcend};6ae50bb56203f2f3875e3ee78efab1a5:f22429107ea7806f54902bb2926c8872
SUNDANCE TV;https://ott.zapitv.com/live/eds_c2/sundance_hd/dash_live_enc/sundance_hd.mpd?begin={utc}&end={utcend};7107df0ecf168438df3d5e35a06f5e8b:1541c20a7dc82b302ec9b97274910162
Global Tendencias;https://ott.zapitv.com/live/eds_c2/tendencias/dash_live_enc/tendencias.mpd?begin={utc}&end={utcend};4867b0cba7d2bd6ccdfc69ba6e37b1aa:75cc9e24449f88fcc0d39eb0cc096937
Global Telenovelas;https://ott.zapitv.com/live/eds_c2/de_telenovelas/dash_live_enc/de_telenovelas.mpd?begin={utc}&end={utcend};bf4671f44116448236c23dc7813c4835:e01ba6e0304c3e0d82b3705e01607a9e
DIVINITY;https://ott.zapitv.com/live/eds_c2/divinity/dash_live_enc/divinity.mpd?begin={utc}&end={utcend};f1ee8e0222e67dcefdcb7ed95a6911f1:a4b37cde4618859146b0278f628997ee
PARAMOUNT;https://ott.zapitv.com/live/eds_c2/paramount_channel/dash_live_enc/paramount_channel.mpd?begin={utc}&end={utcend};46cebb5906150f7e0aadc3a4d93d1a6c:757da1b0cdcf2c54c6c8b1560f272d33
DMAX;https://ott.zapitv.com/live/eds_c2/dmax/dash_live_enc/dmax.mpd?begin={utc}&end={utcend};73e55164b719d1210351f86093bc3ec3:792ffb4e6ebbe2aae394061f01948e40
HISTORIA;https://ott.zapitv.com/live/eds_c2/historia_hd/dash_live_enc/historia_hd.mpd?begin={utc}&end={utcend};8913dddc7f301085c95e19bb94c005a8:ff60fbb41c2148e40c110237554ba652
CANAL ODISEA;https://ott.zapitv.com/live/eds_c2/odisea_hd/dash_live_enc/odisea_hd.mpd?begin={utc}&end={utcend};a7837ebd0bfe0116ce5de21c7bc6158b:dd2decde9c929bddbee7e47bb68cfdca
IBERALIA;https://ott.zapitv.com/live/eds_c2/iberalia/dash_live_enc/iberalia.mpd?begin={utc}&end={utcend};3c91a4e9ccc6f6f253fc9d7c57850aa9:c88cd0613ffed9721c0616583cb917d8
Iberalia 100% Caza;https://ott.zapitv.com/live/eds_c2/iberalia_caza/dash_live_enc/iberalia_caza.mpd?begin={utc}&end={utcend};54be45ed0cc1524243461e2f420310d9:6d1386b01391d3d86f4debf5d9650fe7
Iberalia 100% Pesca;https://ott.zapitv.com/live/eds_c2/iberalia_pesca/dash_live_enc/iberalia_pesca.mpd?begin={utc}&end={utcend};7ae3343806fda8a7bc27d38ab605a702:9a6a18d6877a1cfb037417be8ec3d7e6
DISCOVERY;https://ott.zapitv.com/live/eds_c2/discovery_channel_hd/dash_live_enc/discovery_channel_hd.mpd?begin={utc}&end={utcend};d37f084ced3f48cd8e7ab2250f26030d:7bae03ffb6f8a3539e8f93c0675e9c0a
CANAL COCINA;https://ott.zapitv.com/live/eds_c2/cocina_hd/dash_live_enc/cocina_hd.mpd?begin={utc}&end={utcend};d1622e41b898458f889c697b0de3d1f0:7ad1ffd9308b35d961a6dae3c596fa57
AMC BREAK;https://ott.zapitv.com/live/eds_c2/blaze/dash_live_enc/blaze.mpd?begin={utc}&end={utcend};15e412a4edd85313233969913072e0ff:5098eafaff2b246ee15e8f9aeb5403fb
BuenViaje;https://ott.zapitv.com/live/eds_c2/BUENVIAJE/dash_live_enc/BUENVIAJE.mpd?begin={utc}&end={utcend};05eeec445f9bcfaef03c36965fce16d7:a3b3b1d585f5d0472336a17824d5da22
MTV Hits;https://ott.zapitv.com/live/eds_c2/mtv_hits/dash_live_enc/mtv_hits.mpd?begin={utc}&end={utcend};f2975a79fd099430a195212b04b4dd1e:7f8f21c0b12be72690510d92b893b5ac
MTV 00s;https://ott.zapitv.com/live/eds_c2/vh1/dash_live_enc/vh1.mpd?begin={utc}&end={utcend};999c8a5c8fdd7106a0c4b63cf9bc2223:d9a4c96e3cb098279b5db8f87621fd85
MTV ESPAÑA;https://ott.zapitv.com/live/eds_c2/mtv_espana/dash_live_enc/mtv_espana.mpd?begin={utc}&end={utcend};10f86eedfa603133e035c4c64226dd6b:1678761258b8a16d5d5b9241bd647536
MTV 80s;https://ott.zapitv.com/live/eds_c2/MTV80_S/dash_live_enc/MTV80_S.mpd?begin={utc}&end={utcend};77318e15c3e69e56828e86528df8ff31:aa0dd9bbf74de516e23daaa9d5318cc2
TELEDEPORTE;https://ott.zapitv.com/live/eds_c2/teledeporte_hd/dash_live_enc/teledeporte_hd.mpd?begin={utc}&end={utcend};1937b8f0dc833e0a8f457240972e440d:8cbb79a6410cc0d0d80d148f282afd95
EUROSPORT 1;https://ott.zapitv.com/live/eds_c2/eurosport_1_hd/dash_live_enc/eurosport_1_hd.mpd?begin={utc}&end={utcend};237be8ca9383755e9f5784dd23f545eb:15a723773c3b3cbce295c0aed0bc71c3
EUROSPORT 2;https://ott.zapitv.com/live/eds_c2/eurosport_2_hd/dash_live_enc/eurosport_2_hd.mpd?begin={utc}&end={utcend};15382879a9bcfa6f1a04a86d5b4324e9:664241133368ab039dc1fb15206ba54b
Realmadrid TV;https://ott.zapitv.com/live/eds_c2/real_madrid_tv_hd/dash_live_enc/real_madrid_tv_hd.mpd?begin={utc}&end={utcend};5d875cda9ca113fcea402f659595c5cd:9ccf825fb4548c17a7b7b5da17056208
Surf Channel;https://ott.zapitv.com/live/eds_c2/surf_channel/dash_live_enc/surf_channel.mpd?begin={utc}&end={utcend};4f59b4aefec579d0e2e27acb881b042a:c9d80a33d090b8b31098b78e0a663cda
ENERGY;https://ott.zapitv.com/live/eds_c2/energy/dash_live_enc/energy.mpd?begin={utc}&end={utcend};4a9dbf7992b2f2de807c30928a14eba6:48b9e3073b6c646ef9bfcfa307492e10
24h HD;https://ott.zapitv.com/live/eds_c2/24h_tve/dash_live_enc/24h_tve.mpd?begin={utc}&end={utcend};8b5da8f127efd5a84c8d7d37fc828d44:244f6ea4a4fa570e3cc9c4817cef9a23
EL TORO TV;https://ott.zapitv.com/live/eds_c2/intereconomia/dash_live_enc/intereconomia.mpd?begin={utc}&end={utcend};793c59ba1b09b8a1004da778dab0afcb:80ee84db32af59b25625081db47d247d
EWTN;https://ott.zapitv.com/live/eds_c2/ewtn/dash_live_enc/ewtn.mpd?begin={utc}&end={utcend};e4bdec5857e084486f973410935eff8b:12c2a996a60f4b296effce1b5f457c1c
COMEDY CENTRAL;https://ott.zapitv.com/live/eds_c2/comedy_central/dash_live_enc/comedy_central.mpd?begin={utc}&end={utcend};f8757de5a495ce5db4893c2eefc11e58:d8309cd9fa8c286f277b4cb9841d7bd2
CANAL DECASA;https://ott.zapitv.com/live/eds_c2/decasa_hd/dash_live_enc/decasa_hd.mpd?begin={utc}&end={utcend};0909d9aaca5c6e6a0f1a4ad8e4459f65:eef835f4d956c3e0a794879e7dbe5bdd
DKISS;https://ott.zapitv.com/live/eds_c2/dkiss_tv/dash_live_enc/dkiss_tv.mpd?begin={utc}&end={utcend};a70651586506d7deea68016492dedb94:9b094387d596c64260754f07baeca18c
TEN;https://ott.zapitv.com/live/eds_c2/ten/dash_live_enc/ten.mpd?begin={utc}&end={utcend};55bf0a5d7c5eb6edecd240c0a31e0002:f8e186b29f5b2d162ac08446ee5aa68b
BE MAD;https://ott.zapitv.com/live/eds_c2/bemad_hd/dash_live_enc/bemad_hd.mpd?begin={utc}&end={utcend};3743a0f5f8633002477dbd91510d7794:53d6e6c17b95cab5109a6fea5fd077d7
atreseries HD;https://ott.zapitv.com/live/eds_c2/atreseries_hd/dash_live_enc/atreseries_hd.mpd?begin={utc}&end={utcend};2f9f8aec731ad9b6da84e72df2b318fa:8581c19cf83e9b0a872484377ea8c162
BOM;https://ott.zapitv.com/live/eds_c2/bom/dash_live_enc/bom.mpd?begin={utc}&end={utcend};8ac9b27e3ad295bdd734c7e39ac11c88:be3c7d023415988972512ccba3f14fe4
SQUIRREL;https://ott.zapitv.com/live/eds_c2/squirrel/dash_live_enc/squirrel.mpd?begin={utc}&end={utcend};4e616cc1f21a189fc3b829357acf15c9:77eec11eb17a2f47aad49f3a5e2a0c72
NOVA;https://ott.zapitv.com/live/eds_c2/nova/dash_live_enc/nova.mpd?begin={utc}&end={utcend};2fa4cb9b8c4bf791c9489f14918c3c53:3da828bf72864f063e471630816d1d2e
MEGA;https://ott.zapitv.com/live/eds_c2/mega/dash_live_enc/mega.mpd?begin={utc}&end={utcend};7a70eab585ae43502fc74c80ff36e220:fdf388a77f8e45cc28e8ba7887b8f29a
NEOX;https://ott.zapitv.com/live/eds_c2/neox/dash_live_enc/neox.mpd?begin={utc}&end={utcend};6da74168743cd45b6b65485269dcd050:36453fecd12b91a30958fd340ca1d087
FDF;https://ott.zapitv.com/live/eds_c2/fdf/dash_live_enc/fdf.mpd?begin={utc}&end={utcend};5032cdcff452f508b44fe895808b9cee:51c7c5b35ad30d4d8552143f19fd5e11
DARK;https://ott.zapitv.com/live/eds_c2/DARK_HD/dash_live_enc/DARK_HD.mpd?begin={utc}&end={utcend};ee3899fcba09e6de20355394106ca745:d84b6489ff8e5aeecde84a659c0617b8
AMC CRIME;https://ott.zapitv.com/live/eds_c2/crimen/dash_live_enc/crimen.mpd?begin={utc}&end={utcend};e3048d6cc539b8a8b90d74992fb4e197:4e494e4d179abc3d3f10073b21ac8630
AllFlamenco;https://ott.zapitv.com/live/eds_c2/all_flamenco/dash_live_enc/all_flamenco.mpd?begin={utc}&end={utcend};7c158a75ffdedb3725862bc2781cc37b:21003ef5f3c9cfc278307d6c8329898c
A PUNT HD;https://ott.zapitv.com/live/eds_c2/a_punt_hd/dash_live_enc/a_punt_hd.mpd?begin={utc}&end={utcend};90c720da6eb15228edb8bde37c13be8b:4aa47fc89cd090b3d0851c7dbd2602ee
TELEMADRID;https://ott.zapitv.com/live/eds_c2/tele_madrid_hd/dash_live_enc/tele_madrid_hd.mpd?begin={utc}&end={utcend};3abf39227e2b2ccacd2854730faaf8e2:64a402f23216e311c38ca990e8792f2a
LaOtra;https://ott.zapitv.com/live/eds_c2/la_otra/dash_live_enc/la_otra.mpd?begin={utc}&end={utcend};208049ec2e5bf2e7a5d3e17bbdf2f16f:0dde11377f475bfc203c941e82136360
CMM;https://ott.zapitv.com/live/eds_c2/cmt_hd/dash_live_enc/cmt_hd.mpd?begin={utc}&end={utcend};9be0461082e289bb7991a92e96b4acdd:d8cc8fef100a446b75cd08b93f724980
CANAL SUR HD;https://ott.zapitv.com/live/eds_c2/canal_sur_hd/dash_live_enc/canal_sur_hd.mpd?begin={utc}&end={utcend};56ddc01aebb4bd0bedb0762be969ff87:3eaa3e0e5c394792742f05d57baf6ccd
7RM;https://ott.zapitv.com/live/eds_c2/7rm_hd/dash_live_enc/7rm_hd.mpd?begin={utc}&end={utcend};4867aa61887a973461c3f9f6add0ae4a:c347d26476708fc5ac2fecdcf2a5aabb
CANAL EXTREMADURA;https://ott.zapitv.com/live/eds_c2/extremadura_tv/dash_live_enc/extremadura_tv.mpd?begin={utc}&end={utcend};a96d9a89a109d408c1733d5943b11f1f:b5b64f3a9de3dde22b40e9ebd91dfda7
Moto ADV;https://ott.zapitv.com/live/eds_c2/moto_adv_hd/dash_live_enc/moto_adv_hd.mpd?begin={utc}&end={utcend};047c8158ba826800c3a4b4607d56cbad:3eb58821118274ecc506a7d4b8343715
REKTV;https://ott.zapitv.com/live/eds_c2/REKTV/dash_live_enc/REKTV.mpd?begin={utc}&end={utcend};f2e9efdd9a0b933647fb7a46c26e68fc:f45832f2f37e3727b3dec7f66a7166dd
Torolé;https://ott.zapitv.com/live/eds_c2/torole/dash_live_enc/torole.mpd?begin={utc}&end={utcend};c665d716114f89d3162d0337be3a66d4:fb5d7ee6db86bb87b0312861b8252582
TRECE;https://ott.zapitv.com/live/eds_c2/TRECETV/dash_live_enc/TRECETV.mpd?begin={utc}&end={utcend};67fce2ad7b5af340e31da7c559decdd4:5f92152dc862fdab5eff9abf0b8b6940
DBIKE;https://ott.zapitv.com/live/eds_c2/DBIKE/dash_live_enc/DBIKE.mpd?begin={utc}&end={utcend};5e8b6d0fd7384e1d9988cd977b6409b7:ee9cdffb5f055bf203307398290e36a3
Canal de las estrellas;https://ott.zapitv.com/live/eds_c2/CANAL_DE_LAS_ESTRELLAS/dash_live_enc/CANAL_DE_LAS_ESTRELLAS.mpd?begin={utc}&end={utcend};940a71d465f34a76d17f66bb84ecd749:309d63d8795189c775b45771c3d4a414
De Película;https://ott.zapitv.com/live/eds_c2/DEPELICULAS/dash_live_enc/DEPELICULAS.mpd?begin={utc}&end={utcend};fe67ff953b5d188cbccbe54146873065:7bb77b414fec132cc8d6ac911e3246ef
DEJATE TV;https://ott.zapitv.com/live/eds_c2/DEJATETV/dash_live_enc/DEJATETV.mpd?begin={utc}&end={utcend};e8c88c97f57dd0666030eb4d9390deb8:c6eb65ce319b241bc78b6396d3ac576e
GOL PLAY;https://ott.zapitv.com/live/eds_c2/gol_tv/dash_live_enc/gol_tv.mpd?begin={utc}&end={utcend};33a801fbfd0d4a939a33638b12f59bc7:09764d98c241cd45a3fcea09593e3255
Libertad Digital;https://ott.zapitv.com/live/eds_c2/LIBERTADDIGITAL/dash_live_enc/LIBERTADDIGITAL.mpd?begin={utc}&end={utcend};24b5148fadbda18d7cbeb029381678e2:04890dc761ddcacd82f22cec44c09835
TLnovelas;https://ott.zapitv.com/live/eds_c2/TELENOVELAS/dash_live_enc/TELENOVELAS.mpd?begin={utc}&end={utcend};2a560efbcb6255d48cf98ff54a632f24:ca77a016d3345bd64c94de73bac8bf45
TV3;https://ott.zapitv.com/live/eds_c2/tv3_hd/dash_live_enc/tv3_hd.mpd?begin={utc}&end={utcend};c470ccf82ba9c9a91c2cb828a63cd155:e862da4dc95679234997f06707ecd021
TVG;https://ott.zapitv.com/live/eds_c2/GALICIA/dash_live_enc/GALICIA.mpd?begin={utc}&end={utcend};8d47b106bc099480411379aa3135a985:45589a49327be7e2a0372f29cec240bf
"""

# ========== SISTEMA DE ACTUALIZACIÓN ==========
def descargar_script_actualizado():
    """Descarga la última versión del script y compara con la local"""
    try:
        # Descargar script remoto
        response = requests.get(VERCEL_SCRIPT_URL, timeout=10)
        response.raise_for_status()
        contenido_remoto = response.text
        
        # Leer script local
        with open(__file__, "r", encoding="utf-8") as f:
            contenido_local = f.read()
        
        # Comparar contenidos
        if contenido_remoto.strip() == contenido_local.strip():
            print("\n[INFO] Estás usando la última versión")
            return None
            
        # Guardar actualización si hay diferencias
        with open("script_actualizado.py", "w", encoding="utf-8") as file:
            file.write(contenido_remoto)
        
        print("\n[ACTUALIZACIÓN] Nueva versión detectada!")
        return "script_actualizado.py"
        
    except Exception as e:
        print(f"\n[ERROR] Fallo al verificar actualizaciones: {str(e)}")
        return None

def actualizar_script():
    """Reemplaza el script actual si hay una nueva versión"""
    script_actualizado = descargar_script_actualizado()
    if script_actualizado:
        try:
            os.replace(script_actualizado, __file__)
            print("[ACTUALIZACIÓN] ¡Actualización aplicada con éxito!")
            print("[ACTUALIZACIÓN] Por favor vuelva a ejecutar el script para actualizar")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Fallo al aplicar actualización: {str(e)}")

# Verificar actualizaciones al inicio
actualizar_script()

# ========== FUNCIONES ORIGINALES DEL SCRIPT ==========
def cargar_datos_csv():
    """Carga los datos del CSV integrado en el script"""
    canales = []
    links = {}
    keys = {}
    
    try:
        # Simular lectura de archivo
        reader = csv.reader(io.StringIO(CSV_CONTENT), delimiter=';')
        next(reader)  # Saltar cabecera
        for row in reader:
            if len(row) >= 3:
                nombre = row[0]
                link = row[1]
                key = row[2]
                
                if nombre and link:  # Asegurarse de que hay datos válidos
                    canales.append(nombre)
                    links[nombre] = link
                    keys[nombre] = key
    
        return canales, links, keys
    except Exception as e:
        print(f"Error cargando datos de canales: {str(e)}")
        sys.exit(1)

def obtener_user_agent():
    """Devuelve un User-Agent predeterminado"""
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

def es_horario_verano(fecha):
    """Determina si una fecha está en horario de verano en España"""
    año = fecha.year
    
    # Calcular inicio del horario de verano (último domingo de marzo)
    inicio_verano = datetime.datetime(año, 3, 31)
    while inicio_verano.weekday() != 6:  # 6 es domingo
        inicio_verano -= datetime.timedelta(days=1)
    inicio_verano = inicio_verano.replace(hour=2, minute=0, second=0)
    
    # Calcular fin del horario de verano (último domingo de octubre)
    fin_verano = datetime.datetime(año, 10, 31)
    while fin_verano.weekday() != 6:
        fin_verano -= datetime.timedelta(days=1)
    fin_verano = fin_verano.replace(hour=3, minute=0, second=0)
    
    return inicio_verano <= fecha < fin_verano

def formatear_fechas(fecha_inicio, fecha_fin):
    """Formatea las fechas para usarlas en la URL, convirtiendo de hora local a UTC"""
    try:
        inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%dT%H:%M:%S")
        fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%dT%H:%M:%S")
        
        offset_inicio = 2 if es_horario_verano(inicio_dt) else 1
        offset_fin = 2 if es_horario_verano(fin_dt) else 1
        
        print(f"\n[INFO] Horario detectado:")
        print(f"- Inicio: UTC+{offset_inicio} ({'Verano' if offset_inicio == 2 else 'Invierno'})")
        print(f"- Fin: UTC+{offset_fin} ({'Verano' if offset_fin == 2 else 'Invierno'})")
        
        inicio_utc = inicio_dt - datetime.timedelta(hours=offset_inicio)
        fin_utc = fin_dt - datetime.timedelta(hours=offset_fin)
        
        inicio_utc_str = inicio_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        fin_utc_str = fin_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        
        return inicio_utc_str, fin_utc_str
    except Exception as e:
        print(f"Error al formatear fechas: {str(e)}")
        sys.exit(1)

def extraer_key_decryption(key_string):
    """Extrae la clave de decripción del formato key1:key2"""
    if not key_string:
        return None
    
    parts = key_string.split(':')
    return parts[1] if len(parts) == 2 else key_string

def ejecutar_ffprobe(url, key_decryption):
    """Ejecuta ffprobe para obtener información sobre las pistas disponibles"""
    try:
        # Construir comando base
        comando_base = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]
        
        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', key_decryption])
        
        # Añadir URL
        comando_base.append(url)
        
        print("\n[FFPROBE] Analizando pistas disponibles...")
        result = subprocess.run(comando_base, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"\n[ERROR] FFprobe falló: {result.stderr}")
            return None
        
        return json.loads(result.stdout)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar ffprobe: {str(e)}")
        return None

def seleccionar_mejor_pista(streams_data):
    """Selecciona la pista de video de mayor calidad"""
    if not streams_data or 'streams' not in streams_data:
        print("\n[ERROR] No se encontraron pistas de video para analizar")
        return None
    
    video_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'video']
    if not video_streams:
        print("\n[ERROR] No se encontraron pistas de video")
        return None
    
    # Ordenar por resolución (multiplicar ancho x alto)
    video_streams.sort(key=lambda x: 
        int(x.get('width', 0)) * int(x.get('height', 0)), 
        reverse=True
    )
    
    mejor_pista = video_streams[0]
    print(f"\n[INFO] Mejor pista de video encontrada:")
    print(f"- Índice: {mejor_pista.get('index')}")
    print(f"- Resolución: {mejor_pista.get('width')}x{mejor_pista.get('height')}")
    print(f"- Codec: {mejor_pista.get('codec_name')}")
    print(f"- Bitrate: {int(mejor_pista.get('bit_rate', 0))/1000:.2f} kbps")
    
    return mejor_pista

def mostrar_info_pistas(streams_data):
    """Muestra información sobre todas las pistas disponibles"""
    if not streams_data or 'streams' not in streams_data:
        return
    
    video_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'video']
    audio_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'audio']
    subtitle_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'subtitle']
    
    print("\n[INFO] Pistas disponibles:")
    print(f"- Video: {len(video_streams)} pistas")
    print(f"- Audio: {len(audio_streams)} pistas")
    print(f"- Subtítulos: {len(subtitle_streams)} pistas")
    
    if audio_streams:
        print("\n[INFO] Pistas de audio:")
        for i, audio in enumerate(audio_streams):
            lang = audio.get('tags', {}).get('language', 'desconocido')
            print(f"  {i+1}. Índice: {audio.get('index')}, Idioma: {lang}, Codec: {audio.get('codec_name')}")
    
    if subtitle_streams:
        print("\n[INFO] Pistas de subtítulos:")
        for i, sub in enumerate(subtitle_streams):
            lang = sub.get('tags', {}).get('language', 'desconocido')
            print(f"  {i+1}. Índice: {sub.get('index')}, Idioma: {lang}")

def ejecutar_ffmpeg_mejorado(url, key_decryption, nombre_archivo, streams_data):
    """Ejecuta ffmpeg para descargar y desencriptar el contenido con la mejor pista de video y todas las pistas de audio y subtítulos"""
    try:
        # Mostrar información de todas las pistas
        mostrar_info_pistas(streams_data)
        
        # Obtener la mejor pista de video
        mejor_pista = seleccionar_mejor_pista(streams_data)
        if not mejor_pista:
            return ejecutar_ffmpeg(url, key_decryption, nombre_archivo)  # Usar el método original como fallback
        
        # Construir comando base
        comando_base = [
            'ffmpeg',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]

        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', f'"{key_decryption}"'])

        # Añadir URL de entrada
        comando_final = comando_base + ['-i', f'"{url}"', '-c', 'copy']
        
        # Mapear sólo la mejor pista de video
        comando_final.extend(['-map', f'0:{mejor_pista.get("index")}'])
        
        # Mapear TODAS las pistas de audio
        comando_final.extend(['-map', '0:a'])
        
        # Mapear TODAS las pistas de subtítulos (si existen)
        comando_final.extend(['-map', '0:s?'])
        
        # Añadir nombre del archivo
        comando_final.append(f'"{nombre_archivo}"')

        # Crear versión segura para ejecución (sin comillas internas)
        comando_ejecucion = []
        for item in comando_final:
            comando_ejecucion.append(item.replace('"', ''))

        print("\n[FFMPEG] Comando generado:")
        print(' '.join(comando_final))

        # Ejecutar con shell=False para mayor seguridad
        result = subprocess.run(comando_ejecucion, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] FFmpeg falló con código: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

def ejecutar_ffmpeg(url, key_decryption, nombre_archivo):
    """Función original de ffmpeg como fallback"""
    try:
        # Construir comando base
        comando_base = [
            'ffmpeg',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]

        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', f'"{key_decryption}"'])

        # Añadir parámetros restantes entrecomillados
        comando_final = comando_base + [
            '-i', f'"{url}"',
            '-c', 'copy',
            '-map', '0:v',
            '-map', '0:a',
            '-map', '0:s?',
            f'"{nombre_archivo}"'
        ]

        # Crear versión segura para ejecución (sin comillas internas)
        comando_ejecucion = []
        for item in comando_final:
            comando_ejecucion.append(item.replace('"', ''))

        print("\n[FFMPEG] Comando generado (fallback):")
        print(' '.join(comando_final))

        # Ejecutar con shell=False para mayor seguridad
        result = subprocess.run(comando_ejecucion, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] FFmpeg falló con código: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

def verificar_url(url):
    """Verifica si una URL existe antes de intentar descargarla"""
    try:
        response = requests.head(url, headers={
            "User-Agent": obtener_user_agent(),
            "Referer": "https://ver.zapitv.com"
        }, timeout=10)
        return response.status_code < 400
    except Exception:
        return False

def ejecutar_script():
    """Función principal que ejecuta el script"""
    try:
        canales, links, keys = cargar_datos_csv()
        
        print("\n=== CANALES DISPONIBLES ===")
        for i, canal in enumerate(canales, 1):
            print(f"{i}. {canal}")
        
        try:
            seleccion = int(input("\nIngrese el número del canal: ")) - 1
            if not 0 <= seleccion < len(canales):
                print("Selección inválida")
                return
            canal_seleccionado = canales[seleccion]
        except ValueError:
            print("Ingrese un número válido")
            return
        
        enlace = links.get(canal_seleccionado)
        clave = keys.get(canal_seleccionado)
        
        if not enlace:
            print(f"No hay enlace para {canal_seleccionado}")
            return
        
        print("\n=== FECHAS (Hora Local España) ===")
        fecha_inicio = input("Fecha/hora inicio (YYYY-MM-DDTHH:MM:SS): ")
        fecha_fin = input("Fecha/hora fin (YYYY-MM-DDTHH:MM:SS): ")
        
        inicio_utc, fin_utc = formatear_fechas(fecha_inicio, fecha_fin)
        url_final = enlace.replace("{utc}", inicio_utc).replace("{utcend}", fin_utc)
        clave_decripcion = extraer_key_decryption(clave)
        
        nombre_base = f"{canal_seleccionado.replace(' ', '_')}_{datetime.datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M')}"
        nombre_archivo = input(f"\nNombre del archivo (dejar vacío para '{nombre_base}'): ") or nombre_base
        nombre_archivo += ".ts"
        
        print(f"\n[VERIFICACIÓN] Probando URL...")
        if not verificar_url(url_final):
            print("¡URL no accesible! ¿Continuar? (s/n)")
            if input().lower() != 's':
                return
        
        print("\n=== RESUMEN ===")
        print(f"Canal: {canal_seleccionado}")
        print(f"URL: {url_final}")
        print(f"Archivo: {nombre_archivo}")
        print(f"Clave: {clave_decripcion or 'No requiere'}")
        
        if input("\n¿Iniciar descarga? (s/n): ").lower() != 's':
            print("Descarga cancelada")
            return
        
        print("\n[ANÁLISIS] Obteniendo información de las pistas...")
        streams_data = ejecutar_ffprobe(url_final, clave_decripcion)
        
        print("\n[DESCARGA] Iniciando...")
        if ejecutar_ffmpeg_mejorado(url_final, clave_decripcion, nombre_archivo, streams_data):
            print(f"\n¡Descarga completada! Guardado como: {nombre_archivo}")
        else:
            print("\nError en la descarga")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    while True:
        ejecutar_script()
        if input("\n¿Descargar otro contenido? (s/n): ").lower() != 's':
            break
    print("\n¡Gracias por usar el script! - Script hecho por Archivos M08g")

if __name__ == "__main__":
    main()
