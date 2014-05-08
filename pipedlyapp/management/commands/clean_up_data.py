from django.core.management.base import BaseCommand, CommandError
from pipedlyapp.models import ScrapinghubItem, SemantriaItem, SemantriaPhrase, SemantriaEntity, SemantriaTheme, SemantriaOpinion, SemantriaTopic, SemantriaEntityToThemes

class Command(BaseCommand):
    args = ''
    help = 'Sanitize data'

    def handle(self, *args, **options):
        # Match bad themes
        bad_themes_list = ['Blog Entries','View Articles','Posts']
        for bad_theme in bad_themes_list:
            matches = SemantriaTheme.objects.filter(title__icontains=bad_theme)
            matches.delete()

        bad_entity_list = [r'#[0-9]+']
        for bad_entity in bad_entity_list:
            matches = SemantriaEntity.objects.filter(title__iregex=bad_entity)
            matches.delete()
        

        
