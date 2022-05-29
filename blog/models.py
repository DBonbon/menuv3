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


class HomePage(Page):
    template = "blog/home_page.html"
    introduction = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        context['home_page'] = Page.objects.get().get_children()
        return context

"""
    def get_context(self, request):
        context = super().get_context(request)
        context['blog_index_page'] = Page.objects.get().all()
        return context
"""

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

    parent_page_types = ["blog.BlogIndexPage",]


class BlogIndexPage(Page):
    introduction = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context['menuitems'] = request.self.get_descendants(inclusive=True).live().in_menu()
        #context['menuitems'] = Page.objects.child_of(self)
        

class MenuItem(Orderable):

    link_title = models.CharField(
        blank=True,
        null=True,
        max_length=50
    )
    link_url = models.CharField(
        max_length=500,
        blank=True
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)

    page = ParentalKey("Menu", related_name="menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        FieldPanel("open_in_new_tab"),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title
        return 'Missing Title'
    
    @property    
    def get_context(self, request):
        context = super(HomePage, self).get_context(request)
        context['menuitems'] = request.site.root_page.get_descendants(inclusive=True).live().in_menu()



@register_snippet
class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)
    # slug = models.SlugField()

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Menu"),
        InlinePanel("menu_items", label="Menu Item")
    ]

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