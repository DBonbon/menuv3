from django.db import models
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from modelcluster.models import ClusterableModel
from django_extensions.db.fields import AutoSlugField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel
from wagtail.core.models import Orderable

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.admin.panels import FieldPanel
else:
    from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"


class StoryBlock(blocks.StreamBlock):
    heading = blocks.CharBlock()
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()


@register_snippet
class BlogCategory(TranslatableMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BlogPostPage(Page):
    publication_date = models.DateField(null=True, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True
    )
    body = StreamField(StoryBlock())
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL, null=True, related_name="blog_posts"
    )

    content_panels = Page.content_panels + [
        FieldPanel("publication_date"),
        ImageChooserPanel("image"),
        FieldPanel("body") if WAGTAIL_VERSION >= (3, 0) else StreamFieldPanel("body"),
        SnippetChooserPanel("category"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]


class BlogIndexPage(Page):
    introduction = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = ["home.HomePage"]


@register_snippet
class Menu(ClusterableModel):

    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title', editable=True, help_text="Unique identifier of menu. Will be populated automatically from title of menu. Change only if needed.")

    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('slug'),
        ], heading=("Menu")),
        InlinePanel('menu_items', label=("Menu Item"))
    ]

    def __str__(self):
        return self.title


class MenuItem(Orderable):
    menu = ParentalKey('Menu', related_name='menu_items', help_text=("Menu to which this item belongs"))
    title = models.CharField(max_length=50, help_text=("Title of menu item that will be displayed"))
    link_url = models.CharField(max_length=500, blank=True, null=True, help_text=("URL to link to, e.g. /accounts/signup (no language prefix, LEAVE BLANK if you want to link to a page instead of a URL)"))
    link_page = models.ForeignKey(
        Page, blank=True, null=True, related_name='+', on_delete=models.CASCADE, help_text=("Page to link to (LEAVE BLANK if you want to link to a URL instead)"),
    )
    title_of_submenu = models.CharField(
        blank=True, null=True, max_length=50, help_text=("Title of submenu (LEAVE BLANK if there is no custom submenu)")
    )
    icon = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True, on_delete=models.SET_NULL, related_name='+',
    )
    show_when = models.CharField(
        max_length=15,
        choices=[('always', ("Always")), ('logged_in', ("When logged in")), ('not_logged_in', ("When not logged in"))],
        default='always',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('link_url'),
        PageChooserPanel('link_page'),
        FieldPanel('title_of_submenu'),
        ImageChooserPanel('icon'),
        FieldPanel('show_when'),
    ]

    def trans_page(self, language_code):
        if self.link_page:
            can_page = self.link_page
            if language_code == settings.LANGUAGE_CODE: # requested language is the canonical language
                return can_page
            try:
                language = Language.objects.get(code=language_code)
            except Language.DoesNotExist: # no language found, return original page
                return self.link_page
            return Page.objects.get(language=language, can_page=can_page)
        return None

    def trans_url(self, language_code):
        if self.link_url:
            return '/' + language_code + self.link_url
        elif self.link_page:
            return self.trans_page(language_code).url
        return None

    @property
    def slug_of_submenu(self):
        # becomes slug of submenu if there is one, otherwise None
        if self.title_of_submenu:
            return slugify(self.title_of_submenu)
        return None

    def show(self, authenticated):
        return ((self.show_when == 'always')
                or (self.show_when == 'logged_in' and authenticated)
                or (self.show_when == 'not_logged_in' and not authenticated))

    def __str__(self):
        return self.title


@register_snippet
class CompanyLogo(models.Model):
    name = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('name', classname='full'),
        ImageChooserPanel('logo'),
    ]

    def __str__(self):
        return self.name