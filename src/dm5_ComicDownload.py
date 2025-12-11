#-*- coding: utf-8
"""
requirements:
    PyExecJS
    requests
"""
import sys, os, re, requests, execjs
from bs4 import BeautifulSoup

debug_Flag = True
OUT_DIR = r'output/'
DM5_URL = r'http://www.dm5.com/'
HTTP_OK = 200
# Number of threads for image downloading
NUM_THREADS = 5  # Change this value to configure thread count

class Comic_Context:
    def __init__( self ):
        self.Title = ''
        self.Max_Page = -1
        self.Save_Path = ''
        self.Next_Chapter = ''        
        self.Chapter_Count = 0        
        self.DM5_CID = ''
        self.DM5_VIEWSIGN = ''
        self.DM5_VIEWSIGN_DT = ''
comic_Context = Comic_Context()   

def debug_print( debug_info ):
    if debug_Flag:
        print( f'debug_info: {debug_info}' )

def make_path( save_path ):
    os.makedirs( save_path, exist_ok=True )

def get_next_chapter( soup ):
    element = soup.find('div', {'class': 'view-paging'})
    if element is None:        
        return ''

    element_NextChapter = element.find_all( 'a', {'class': 'block'} )

    next_chapter = element_NextChapter[-1]['href'][1:]
    pattern = r'^m\d+/$'
    match_result = re.fullmatch( pattern, next_chapter )
    if match_result:
        return next_chapter
    return ''

def get_comic_context( soup ):    
    js_Codes = soup.find_all('script', {'type': 'text/javascript'})
    js_Vals = {}
    for js_Code in js_Codes:
        if js_Code.text.find( 'var COMIC_MID' ) == -1:
            continue
        pattern = r'var\s+(\w+)\s*=\s*(["\']?)(.*?)\2\s*;'
        matches = re.findall( pattern, js_Code.text )
        js_Vals = { var_name: value.strip() for var_name, _, value in matches }
        break
    
    if not 'DM5_CTITLE' in js_Vals:
        return 
    global comic_Context
    comic_Context.Title = js_Vals[ 'DM5_CTITLE' ]
    comic_Context.Max_Page = js_Vals[ 'DM5_IMAGE_COUNT' ]
    comic_Context.DM5_CID = js_Vals[ 'DM5_CID' ]
    comic_Context.DM5_MID = js_Vals[ 'DM5_MID' ]
    comic_Context.DM5_VIEWSIGN = js_Vals[ 'DM5_VIEWSIGN' ]
    comic_Context.DM5_VIEWSIGN_DT = js_Vals[ 'DM5_VIEWSIGN_DT' ]

def generate_HTTP_JSKeyHeader( url ):
    dm5_header = { 'Accept': r'*/*', \
               'Accept-Language': 'en-US,en;q=0.5', \
               'Connection'     : 'keep-alive', \
               'Host'           : 'www.dm5.com', \
               'Priority'       : 'u=0', \
               'Referer'        : 'https://www.dm5.com/m1678594/', \
               'Sec-Fetch-Dest' : 'empty', \
               'Sec-Fetch-Mode' : 'cors', \
               'Sec-Fetch-Site' : 'same-origin', \
               'User-Agent'     : r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0', \
               'X-Requested-With' : 'XMLHttpRequest'
    }
    return dm5_header

def generate_HTTP_PicHeader( url ):
    dm5_header = { 'User-Agent' : r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0', \
               'Accept'         : 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5', \
               'Accept-Language': 'en-US,en;q=0.5', \
               'Accept-Encoding': 'gzip, deflate, br, zstd', \
               'Connection'     : 'keep-alive', \
               'Referer'        : 'https://www.dm5.com/', \
               'Sec-Fetch-Dest' : 'image', \
               'Sec-Fetch-Mode' : 'no-cors', \
               'Sec-Fetch-Site' : 'cross-site', \
               'Priority'       : 'u=5, i'
    }
    return dm5_header

def download_image( cid, mid, dm5_Sign, dm5_sign_dt, page_Index, chapter_Index ):
    url = f'http://www.dm5.com/m{cid}/'

    key_url = f'https://www.dm5.com/m{cid}/chapterfun.ashx?cid={cid}&page={page_Index}&key=&language=1&gtk=6&_cid={cid}'
    key_url += f'&_mid={mid}&_dt={dm5_sign_dt}&_sign={dm5_Sign}'
    # Download JS code to generate the real picture URL
    js_content = requests.get( key_url, headers = generate_HTTP_JSKeyHeader( url ) ).text
    pic_url = execjs.eval(js_content)

    img_savePath = f'{comic_Context.Save_Path}/{chapter_Index}/'
    make_path( img_savePath )
    if len( pic_url ) == 0:
        print( 'No picture URL was returned!!!' )
        return False

    url = pic_url[0]
    response = requests.get( url, headers = generate_HTTP_PicHeader( url ) )
    if response.status_code == HTTP_OK:
        with open( img_savePath + f'{page_Index}.jpg', 'wb' ) as imgFile:
            imgFile.write( response.content )
    return True    

def donwload_chapter():
    import concurrent.futures
    global comic_Context
    while comic_Context.Next_Chapter != '':
        #if comic_Context.Chapter_Count == 2:
        #    break

        dm5_url = DM5_URL + comic_Context.Next_Chapter
        content = requests.get( dm5_url ).content
        soup = BeautifulSoup( content, 'html.parser' )

        get_comic_context( soup )

        comic_Context.Chapter_Count += 1
        if comic_Context.Chapter_Count == 1:
            comic_Context.Save_Path = OUT_DIR + comic_Context.Next_Chapter
            make_path( comic_Context.Save_Path )
        print( f'Title: { comic_Context.Title }' ) 
        print( f'------>  Fetching page list for chapter { comic_Context.Chapter_Count }' )    
        print( f'------>  Total page { comic_Context.Max_Page }' )

        # Use ThreadPoolExecutor to download images in parallel while honoring early failure
        page_range = range(1, int(comic_Context.Max_Page) + 1)  # Change to: range(1, int(comic_Context.Max_Page) + 1) for full download
        max_workers = max(1, NUM_THREADS)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            pending = {}
            failure_detected = False
            page_iter = iter(page_range)

            def schedule_work():
                while not failure_detected and len(pending) < max_workers:
                    try:
                        page_index = next(page_iter)
                    except StopIteration:
                        break
                    future = executor.submit(
                        download_image,
                        comic_Context.DM5_CID,
                        comic_Context.DM5_MID,
                        comic_Context.DM5_VIEWSIGN,
                        comic_Context.DM5_VIEWSIGN_DT,
                        page_index,
                        comic_Context.Chapter_Count
                    )
                    pending[future] = page_index

            schedule_work()
            while pending:
                done, _ = concurrent.futures.wait(
                    pending.keys(),
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                for future in done:
                    page_index = pending.pop(future)
                    try:
                        result = future.result()
                        print(f"------> Fetched image {page_index} {'OK' if result else 'FAILED'}")
                        if not result:
                            failure_detected = True
                    except Exception as exc:
                        failure_detected = True
                        print(f"------> Fetched image {page_index} generated an exception: {exc}")
                if failure_detected:
                    for future in pending:
                        future.cancel()
                    break
                schedule_work()

        print( '------------------------------------------------------------------------' )
        comic_Context.Next_Chapter = get_next_chapter( soup )

def download_comic( url ):
    pat_url = r'http:\/\/www\.dm5\.com\/m\d+(-p\d+)?\/'
    if not re.match( pat_url, url ):
        print( f'Not a valid dm5 url: {url}' )
        return
     
    print( f'Fetching comic from: {url}' )

    pat_url = r'dm5\.com/(\w+)/'
    
    global comic_Context
    comic_Context.Next_Chapter = re.findall( pat_url, url )[0]

    donwload_chapter()
    print( f'Finish fetching comic { comic_Context.Title }' )

if __name__ == '__main__':
    if len( sys.argv ) > 1:
        url = sys.argv[1]
    else:
        print( 'Usage: crawler_dm5_com.py <url>' )
        exit 

    download_comic( url )



