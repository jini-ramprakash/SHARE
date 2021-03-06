from share.normalize import *
from share.normalize import links


class Link(Parser):
    url = ctx
    type = RunPython('get_link_type', ctx)

    def get_link_type(self, link):
        if 'dx.doi.org' in link:
            return 'doi'
        if 'id.crossref.org' in link:
            return 'provider'
        return 'misc'


class ThroughLinks(Parser):
    link = Delegate(Link, ctx)


class Publisher(Parser):
    name = ctx


class Funder(Parser):
    name = ctx.name

    class Extra:
        doi = Maybe(ctx, 'DOI')
        award = Maybe(ctx, 'award')
        doi_asserted_by = Maybe(ctx, 'doi-asserted-by')


class Association(Parser):
    pass


class Organization(Parser):
    name = Maybe(ctx, 'name')


class Affiliation(Parser):
    pass


class Identifier(Parser):
    url = Orcid(ctx)
    base_url = Static('https://orcid.org')


class ThroughIdentifiers(Parser):
    identifier = Delegate(Identifier, ctx)


class Person(Parser):
    given_name = Maybe(ctx, 'given')
    family_name = Maybe(ctx, 'family')
    affiliations = Map(Delegate(Affiliation.using(entity=Delegate(Organization))), Maybe(ctx, 'affiliation'))
    identifiers = Map(Delegate(ThroughIdentifiers), Maybe(ctx, 'ORCID'))


class Contributor(Parser):
    person = Delegate(Person, ctx)
    order_cited = ctx('index')
    cited_name = links.Join(
        Concat(
            Maybe(ctx, 'given'),
            Maybe(ctx, 'family')
        ),
        joiner=' '
    )


class Tag(Parser):
    name = ctx


class ThroughTags(Parser):
    tag = Delegate(Tag, ctx)


class CreativeWork(Parser):
    """
    Documentation for CrossRef's metadata can be found here:
    https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md
    """

    title = Maybe(ctx, 'title')[0]
    description = Maybe(ctx, 'subtitle')[0]
    date_updated = ParseDate(Try(ctx.deposited['date-time']))

    contributors = Map(
        Delegate(Contributor),
        Maybe(ctx, 'author')
    )
    links = Map(Delegate(ThroughLinks), DOI(ctx.DOI))
    publishers = Map(
        Delegate(Association.using(entity=Delegate(Publisher))),
        ctx.publisher
    )
    funders = Map(
        Delegate(Association.using(entity=Delegate(Funder))),
        Maybe(ctx, 'funder')
    )
    # TODO These are "a controlled vocabulary from Sci-Val", map to Subjects!
    tags = Map(
        Delegate(ThroughTags),
        Maybe(ctx, 'subject')
    )

    class Extra:
        alternative_id = Maybe(ctx, 'alternative-id')
        archive = Maybe(ctx, 'archive')
        article_number = Maybe(ctx, 'article-number')
        chair = Maybe(ctx, 'chair')
        container_title = Maybe(ctx, 'container-title')
        date_created = ParseDate(Try(ctx.created['date-time']))
        # TODO move date_published out of extra?
        date_published = Maybe(ctx, 'issued')
        editor = Maybe(ctx, 'editor')
        licenses = Maybe(ctx, 'license')
        isbn = Maybe(ctx, 'isbn')
        issn = Maybe(ctx, 'issn')
        issue = Maybe(ctx, 'issue')
        reference_count = ctx['reference-count']
        member = Maybe(ctx, 'member')
        page = Maybe(ctx, 'page')
        published_online = Maybe(ctx, 'published-online')
        published_print = Maybe(ctx, 'published-print')
        subjects = Maybe(ctx, 'subject')
        subtitles = Maybe(ctx, 'subtitle')
        titles = ctx.title
        translator = Maybe(ctx, 'translator')
        type = ctx.type
        volume = Maybe(ctx, 'volume')


class Publication(CreativeWork):
    pass


# TODO when DataSet is added
# class DataSet(CreativeWork):
#     pass


class CrossRefNormalizer(Normalizer):
    def do_normalize(self, data):
        unwrapped = self.unwrap_data(data)

        if unwrapped['type'] == 'journal-article':
            return Publication(unwrapped).parse()
        # if unwrapped['type'] == 'dataset':
        #    return DataSet(unwrapped).parse()
        return CreativeWork(unwrapped).parse()
