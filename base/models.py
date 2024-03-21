from datetime import date

from auditlog.registry import auditlog
from dateutil import relativedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from softdelete.models import SoftDeleteObject


# Create your models here.
class TimeStampModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        abstract = True


# PERSON
class Person(models.Model):

    CITYS = (
        (1, "ASUNCION"),
        (2, "FUERTE OLIMPO"),
        (3, "LA VICTORIA"),
        (4, "MCAL ESTIGARRIBIA"),
        (5, "FILADELFIA"),
        (6, "LOMA PLATA"),
        (7, "JOSE FALCON"),
        (8, "NANAWA"),
        (9, "VILLA HAYES"),
        (10, "BENJAMIN ACEVAL"),
        (11, "PINASCO"),
        (12, "CORPUS CHRISTI"),
        (13, "CURUGUATY"),
        (14, "FRANCISCO CABALLERO A"),
        (15, "ITANARA"),
        (16, "KATUETE"),
        (17, "LA PALOMA"),
        (18, "NUEVA ESPERANZA"),
        (19, "SALTOS DEL GUAIRA"),
        (20, "YGATIMI"),
        (21, "YPEJHU"),
        (22, "PEDRO J CABALLERO"),
        (23, "CAPITAN BADO"),
        (24, "BELLA VISTA NORTE"),
        (25, "ALBERDI"),
        (26, "CERRITO"),
        (27, "DESMOCHADOS"),
        (28, "GRAL DIAZ"),
        (29, "GUAZU CUA"),
        (30, "HUMAITA"),
        (31, "ISLA UMBU"),
        (32, "LAURELES"),
        (33, "MAYOR MARTINEZ"),
        (34, "PASO DE PATRIA"),
        (35, "PILAR"),
        (36, "SAN JUAN NEEMBUCU"),
        (37, "TACUARAS"),
        (38, "VILLA FRANCA"),
        (39, "VILLA OLIVA"),
        (40, "VILLALBIN"),
        (41, "AREGUA"),
        (42, "CAPIATA"),
        (43, "FERNANDO DE LA MORA"),
        (44, "GUARAMBARE"),
        (45, "ITA"),
        (46, "ITAUGUA"),
        (47, "J A SALDIVAR"),
        (48, "LAMBARE"),
        (49, "LIMPIO"),
        (50, "LUQUE"),
        (51, "MARIANO R ALONSO"),
        (52, "NUEVA ITALIA"),
        (53, "NEMBY"),
        (54, "SAN ANTONIO"),
        (55, "SAN LORENZO"),
        (56, "VILLA ELISA"),
        (57, "VILLETA"),
        (58, "YPACARAI"),
        (59, "YPANE"),
        (60, "LOS CEDRALES"),
        (61, "CIUDAD DEL ESTE"),
        (62, "DOMINGO M IRALA"),
        (63, "HERNANDARIAS"),
        (64, "IRUNA"),
        (65, "ITAKYRY"),
        (66, "MBARACAYU"),
        (67, "MINGA GUAZU"),
        (68, "MINGA PORA"),
        (69, "NARANJAL"),
        (70, "NACUNDAY"),
        (71, "JUAN E OLEARY"),
        (72, "PTE FRANCO"),
        (73, "SAN ALBERTO"),
        (74, "SAN CRISTOBAL"),
        (75, "SANTA RITA"),
        (76, "SANTA ROSA MONDAY"),
        (77, "YGUAZU"),
        (78, "ACAHAY"),
        (79, "CAAPUCU"),
        (80, "CABALLERO"),
        (81, "CARAPEGUA"),
        (82, "ESCOBAR"),
        (83, "LA COLMENA"),
        (84, "MBUYAPEY"),
        (85, "PARAGUARI"),
        (86, "PIRAYU"),
        (87, "QUIINDY"),
        (88, "QUYQUYHO"),
        (89, "ROQUE GONZALEZ"),
        (90, "SAPUCAI"),
        (91, "TEBICUARYMI"),
        (92, "YAGUARON"),
        (93, "YBYCUI"),
        (94, "YBYTYMI"),
        (95, "VILLA FLORIDA"),
        (96, "SAN MIGUEL"),
        (97, "SAN JUAN BAUTISTA"),
        (98, "SANTA MARIA"),
        (99, "SAN IGNACIO"),
        (100, "SANTA ROSA MISIONES"),
        (101, "SAN PATRICIO"),
        (102, "SANTIAGO"),
        (103, "AYOLAS"),
        (104, "YABEBYRY"),
        (105, "ALTO VERA"),
        (106, "BELLA VISTA SUR"),
        (107, "CAMBYRETA"),
        (108, "CAPITAN MEZA"),
        (109, "CAPITAN MIRANDA"),
        (110, "CARLOS A LOPEZ"),
        (111, "CARMEN PARANA"),
        (112, "CNEL BOGADO"),
        (113, "EDELIRA"),
        (114, "ENCARNACION"),
        (115, "FRAM"),
        (116, "ARTIGAS"),
        (117, "GRAL DELGADO"),
        (118, "HOHENAU"),
        (119, "ITAPUA POTY"),
        (120, "JESUS"),
        (121, "LA PAZ"),
        (122, "LEANDRO OVIEDO"),
        (123, "NATALIO"),
        (124, "NUEVA ALBORADA"),
        (125, "OBLIGADO"),
        (126, "MAYOR OTANO"),
        (127, "PIRAPO"),
        (128, "SAN COSME Y DAMIAN"),
        (129, "SAN JUAN PARANA"),
        (130, "SAN PEDRO PARANA"),
        (131, "SAN RAFAEL DEL PARANA"),
        (132, "TOMAS ROMERO PEREIRA"),
        (133, "TRINIDAD"),
        (134, "YATYTAY"),
        (135, "ABAI"),
        (136, "BERTONI"),
        (137, "BUENA VISTA"),
        (138, "CAAZAPA"),
        (139, "MACIEL"),
        (140, "GRAL MORINIGO"),
        (141, "SAN JUAN NEPOMUCENO"),
        (142, "TAVAI"),
        (143, "YEGROS"),
        (144, "YUTY"),
        (145, "3 DE FEBRERO"),
        (146, "CAAGUAZU"),
        (147, "CARAYAO"),
        (148, "CECILIO BAEZ"),
        (149, "CNEL OVIEDO"),
        (150, "JOSE D OCAMPOS"),
        (151, "J E ESTIGARRIBIA"),
        (152, "JUAN M FRUTOS"),
        (153, "LA PASTORA"),
        (154, "MCAL LOPEZ"),
        (155, "NUEVA LONDRES"),
        (156, "RI3 CORRALES"),
        (157, "RAUL A OVIEDO"),
        (158, "REPATRIACION"),
        (159, "SAN JOAQUIN"),
        (160, "SAN JOSE ARROYOS"),
        (161, "SIMON BOLIVAR"),
        (162, "SANTA ROSA MBUTUY"),
        (163, "VAQUERIA"),
        (164, "YHU"),
        (165, "BORJA"),
        (166, "DR BOTRELL"),
        (167, "CNEL MARTINEZ"),
        (168, "COL INDEPENDENCIA"),
        (169, "FELIX PEREZ CARDOZO"),
        (170, "GRAL GARAY"),
        (171, "ITAPE"),
        (172, "ITURBE"),
        (173, "FASSARDI"),
        (174, "MBOCAYATY"),
        (175, "NATALICIO TALAVERA"),
        (176, "NUMI"),
        (177, "PASO YOBAI"),
        (178, "SAN SALVADOR"),
        (179, "TROCHE"),
        (180, "VILLARRICA"),
        (181, "YATAITY"),
        (182, "ALTOS"),
        (183, "ARROYOS Y ESTEROS"),
        (184, "ATYRA"),
        (185, "CAACUPE"),
        (186, "CARAGUATAY"),
        (187, "EMBOSCADA"),
        (188, "EUSEBIO AYALA"),
        (189, "ISLA PUCU"),
        (190, "ITACURUBI CORDILLERA"),
        (191, "JUAN DE MENA"),
        (192, "LOMA GRANDE"),
        (193, "MBOCAYATY DEL YHAGUY"),
        (194, "NUEVA COLOMBIA"),
        (195, "PIRIBEBUY"),
        (196, "PRIMERO DE MARZO"),
        (197, "SAN BERNARDINO"),
        (198, "SAN JOSE OBRERO"),
        (199, "SANTA ELENA"),
        (200, "TOBATI"),
        (201, "VALENZUELA"),
        (202, "25 DE DICIEMBRE"),
        (203, "ANTEQUERA"),
        (204, "GRAL AQUINO"),
        (205, "CAPIIBARY"),
        (206, "CHORE"),
        (207, "GRAL RESQUIN"),
        (208, "GUAYAIBI"),
        (209, "ITACURUBI ROSARIO"),
        (210, "LIMA"),
        (211, "NUEVA GERMANIA"),
        (212, "SAN ESTANISLAO"),
        (213, "SAN PABLO"),
        (214, "SAN PEDRO YCUAMANDYYU"),
        (215, "SANTA ROSA DEL AGUARAY"),
        (216, "TACUATI"),
        (217, "UNION"),
        (218, "VILLA DEL ROSARIO"),
        (219, "YATAITY DEL NORTE"),
        (220, "SAN LAZARO"),
        (221, "BELEN"),
        (222, "CONCEPCION"),
        (223, "HORQUETA"),
        (224, "LORETO"),
        (225, "SAN CARLOS"),
        (226, "YBY YAU"),
        (227, "JUAN LEON MALLORQUIN"),
        (228, "AZOTE Y"),
        (229, "ZANJA PYTA"),
        (230, "SGTO.JOSE FELIX LOPEZ"),
        (231, "BAHIA NEGRA"),
        (232, "TTE 1 IRALA FERNANDEZ"),
        (233, "TTE.ESTEBAN MARTINEZ"),
        (234, "GRAL.BRUGUEZ"),
        (235, "LIBERACION"),
        (236, "YRYVU CUA"),
        (237, "YASY KAÑY"),
        (238, "YBYRAROBANA"),
        (239, "NUEVA TOLEDO"),
        (240, "TEMBIAPORA"),
        (241, "TEBICUARY"),
        (242, "TAVAPY"),
        (243, "SANTA FE DEL PARANA"),
        (244, "3 DE MAYO"),
        (245, "CARMELO PERALTA"),
        (246, "RAUL PEÑA"),
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        blank=False, null=False
    )
    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=100,
        blank=False, null=False
    )
    birth_date = models.DateField(
        verbose_name=_('Birth Date'),
        blank=True, null=True,
    )
    MALE_CODE = 0
    FEMALE_CODE = 1

    SEX_CODES = (
        (MALE_CODE, _('Male')),
        (FEMALE_CODE, _('Female')),
    )
    sex = models.IntegerField(
        verbose_name=_('Sex'),
        choices=SEX_CODES,
        null=False, blank=False
    )
    weight = models.FloatField(
        verbose_name=_('Weight'),
        blank=True, null=True
    )
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=False, null=True
    )
    document_number = models.CharField(
        verbose_name=_('Document Number'),
        unique=True,
        max_length=10,
        blank=False, null=False
    )
    is_taxpayer = models.BooleanField(
        verbose_name=_('Is Taxpayer'), default=True, null=True, blank=False
    )
    tax_identification_name = models.CharField(
        verbose_name=_('Tax Identification Name'),
        max_length=150,
        blank=False, null=True
    )
    tax_identification_number = models.CharField(
        verbose_name=_('Tax Identification Number'),
        max_length=15,
        blank=False, null=True
    )
    address = models.CharField(
        verbose_name=_('Address'),
        max_length=150,
        blank=False, null=True
    )
    city = models.IntegerField(
        verbose_name=_('City'),
        null=True, blank=True,
        choices=CITYS,
        default=1
    )
    phone_number = models.CharField(
        verbose_name=_('Phone Number'),
        max_length=20,
        null=True, blank=False
    )

    class Meta:
        abstract = True

    def calculate_age(self):
        born = self.birth_date
        if born:
            today = date.today()
            delta = relativedelta.relativedelta(today, born)
            return str(delta.years) + ' años, ' + str(delta.months) + " meses, y " + str(delta.days) + " días."
        else:
            return '---'


# CURRENCY
class Currency(SoftDeleteObject, TimeStampModel):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        blank=False, null=False
    )
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=3,
        null=False, blank=False
    )
    sufix = models.CharField(
        verbose_name=_('Sufix'),
        max_length=3,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencys')

    def __str__(self):
        return self.name


auditlog.register(Currency)


class UserPrintTagConfiguration(SoftDeleteObject, TimeStampModel):
    user = models.OneToOneField(
        verbose_name=_('User'),
        to=User, on_delete=models.PROTECT,
        null=False, blank=False,
        related_name='user_print_configuration',
        unique=True
    )
    name_x = models.FloatField(
        verbose_name=_('Name X'),
        null=False, blank=False
    )
    name_y = models.FloatField(
        verbose_name=_('Name Y'),
        null=False, blank=False
    )
    last_name_x = models.FloatField(
        verbose_name=_('Last Name X'),
        null=False, blank=False
    )
    last_name_y = models.FloatField(
        verbose_name=_('Last Name Y'),
        null=False, blank=False
    )
    date_x = models.FloatField(
        verbose_name=_('Date X'),
        null=False, blank=False
    )
    date_y = models.FloatField(
        verbose_name=_('Date Y'),
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('User Print Tag Configuration')
        verbose_name_plural = _('Users Print Tag Configurations')

    def __str__(self):
        return str(self.user) + ": Configuracion de impresion de etiqueta."


auditlog.register(UserPrintTagConfiguration)
