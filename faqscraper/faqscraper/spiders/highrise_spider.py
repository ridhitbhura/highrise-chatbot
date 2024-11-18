import scrapy

class HighriseSpider(scrapy.Spider):
    name = 'highrise'
    start_urls = ['https://support.highrise.game/en/']
    
    def parse(self, response):
        # Extract all collection links and titles
        collections = response.css('a.collection-link')
        
        for collection in collections:
            collection_data = {
                'collection_url': collection.css('::attr(href)').get(),
                'collection_title': collection.css('div.text-md::text').get().strip(),
                'article_count': collection.css('span.text-base::text').get().strip()
            }
            
            yield response.follow(
                collection_data['collection_url'], 
                callback=self.parse_collection,
                meta={'collection_data': collection_data}
            )

    def parse_collection(self, response):
        collection_data = response.meta['collection_data']
        articles = response.css('section.flex a[data-testid="article-link"]')
        
        for article in articles:
            article_data = {
                'article_url': article.css('::attr(href)').get(),
                'article_title': article.css('span.text-md::text').get().strip(),
                'collection_title': collection_data['collection_title'],
                'collection_url': collection_data['collection_url']
            }
            
            yield response.follow(
                article_data['article_url'],
                callback=self.parse_article,
                meta={'article_data': article_data}
            )

    def parse_article(self, response):
        article_data = response.meta['article_data']
        
        # Get the main article content
        article = response.css('main article')
        structured_content = []
        
        # Process each content block
        for div in article.css('div[class^="intercom-interblocks-"]'):
            content_type = None
            content = None
            
            # Determine content type and extract content
            if 'heading' in div.attrib['class']:
                content_type = 'heading'
                content = div.css('h1::text').get()
            elif 'subheading' in div.attrib['class']:
                content_type = 'subheading'
                content = div.css('h2::text').get()
            elif 'paragraph' in div.attrib['class']:
                content_type = 'paragraph'
                content = div.css('p::text').get()
                # Skip empty paragraphs
                if content and content.strip() == "":
                    continue
            elif 'image' in div.attrib['class']:
                content_type = 'image'
                img_src = div.css('img::attr(src)').get()
                if img_src:
                    content = {
                        'src': img_src,
                        'alignment': 'center' if 'align-center' in div.attrib['class'] else 'left'
                    }
            elif 'horizontal-rule' in div.attrib['class']:
                content_type = 'divider'
                content = '---'
                
            if content_type and content:
                structured_content.append({
                    'type': content_type,
                    'content': content
                })
        
        # Get related articles
        related_articles = [
            {
                'title': article.css('span.text-md::text').get().strip(),
                'url': article.css('::attr(href)').get()
            }
            for article in response.css('section.flex a[data-testid="article-link"]')
        ]
        
        article_data.update({
            'structured_content': structured_content,
            'related_articles': related_articles,
            'timestamp': response.css('time::attr(datetime)').get()
        })
        
        yield article_data