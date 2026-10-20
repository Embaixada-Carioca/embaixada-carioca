import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const source=await readFile(new URL('../functions/[[path]].js',import.meta.url),'utf8');
const {onRequest}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const cases=[
 ['/en','/en/'], ['/es','/es/'], ['/cafe-manha.html','/cafe-da-manha.html'],
 ['/pao-bondinho.html','/parque-bondinho.html'],
 ['/es/donde-comer-cerca-al-pan-de-azucar.html','/es/donde-comer-cerca-del-pan-de-azucar.html'],
 ['/es/donde-comer-cerca-de-pan-de-azucar','/es/donde-comer-cerca-del-pan-de-azucar.html'],
 ['/es/o-que-fazer-depois-do-bondinho-pao-de-acucar/','/es/o-que-fazer-depois-do-bondinho-pao-de-acucar.html'],
 ['/es/como-chegar.html','/es/como-llegar.html'],
];
for(const [path,destination] of cases){
 let assetReads=0;
 const response=await onRequest({request:new Request('https://www.embaixadacarioca.com'+path+'?utm_source=test'),env:{ASSETS:{fetch(){assetReads++;throw Error('Redirect must precede asset fetch');}}},next(){throw Error('Redirect missing');}});
 assert.equal(response.status,301);assert.equal(response.headers.get('Location'),destination+'?utm_source=test');assert.equal(assetReads,0);
}
for(const path of ['/en/','/es/','/cardapio.html']){
 const response=await onRequest({request:new Request('https://www.embaixadacarioca.com'+path),env:{ASSETS:{fetch:async()=>new Response('<h1>Page</h1>')}},next(){throw Error('Stored page missing');}});
 assert.equal(response.status,200);assert.match(response.headers.get('Content-Type'),/text\/html/);
}
const unknown=await onRequest({request:new Request('https://www.embaixadacarioca.com/missing'),env:{ASSETS:{fetch:async()=>new Response('Not found',{status:404})}},next:()=>new Response('Not found',{status:404})});
assert.equal(unknown.status,404);

// Revalidation by browsers and crawlers (If-None-Match) must answer 304 or 200, never an empty 404.
const etag='"v1"';
const conditionalAssets={fetch:async(request)=>{
 assert.equal(request.headers.get('Range'),null,'Range must not reach the asset lookup');
 if(request.headers.get('If-None-Match')===etag)return new Response(null,{status:304,headers:{ETag:etag}});
 return new Response('<h1>Page</h1>',{headers:{ETag:etag}});
}};
for(const path of ['/','/en/','/cardapio.html']){
 const fresh=await onRequest({request:new Request('https://www.embaixadacarioca.com'+path,{headers:{'If-None-Match':etag}}),env:{ASSETS:conditionalAssets},next(){throw Error('Revalidation fell through to a 404');}});
 assert.equal(fresh.status,304);assert.equal(fresh.headers.get('ETag'),etag);
 const changed=await onRequest({request:new Request('https://www.embaixadacarioca.com'+path,{headers:{'If-None-Match':'"old"'}}),env:{ASSETS:conditionalAssets},next(){throw Error('Changed page fell through to a 404');}});
 assert.equal(changed.status,200);assert.match(await changed.text(),/Page/);
 const ranged=await onRequest({request:new Request('https://www.embaixadacarioca.com'+path,{headers:{Range:'bytes=0-10'}}),env:{ASSETS:conditionalAssets},next(){throw Error('Range request fell through to a 404');}});
 assert.equal(ranged.status,200);
}

// Unknown pages show the site's 404 page with status 404; unknown assets stay plain 404s.
const notFoundAssets={fetch:async(request)=>new URL(request.url).pathname==='/_html/404.html.txt'?new Response('<h1>Página não encontrada</h1>',{headers:{ETag:'"404"'}}):new Response('Not found',{status:404})};
const missingPage=await onRequest({request:new Request('https://www.embaixadacarioca.com/pagina-antiga',{headers:{Accept:'text/html,application/xhtml+xml'}}),env:{ASSETS:notFoundAssets},next:()=>new Response(null,{status:404})});
assert.equal(missingPage.status,404);assert.match(missingPage.headers.get('Content-Type'),/text\/html/);assert.match(await missingPage.text(),/Página não encontrada/);assert.equal(missingPage.headers.get('ETag'),null);
const missingAsset=await onRequest({request:new Request('https://www.embaixadacarioca.com/assets/missing.webp',{headers:{Accept:'image/webp,*/*'}}),env:{ASSETS:notFoundAssets},next:()=>new Response(null,{status:404})});
assert.equal(missingAsset.status,404);assert.equal(await missingAsset.text(),'');

// Consolidation of 2026-10-20: every merged page answers one 301 to its main page, with or without ".html".
const block=source.slice(source.indexOf('// Consolidação de 20/10/2026'),source.indexOf(']);'));
const merged=[...block.matchAll(/\["([^"]+)", "([^"]+)"\]/g)].map(m=>[m[1],m[2]]);
assert.equal(merged.length,32,'expected 32 consolidated URLs');
const noAssets={fetch(){throw Error('Redirect must precede asset fetch');}};
for(const [from,to] of merged){
 const direct=await onRequest({request:new Request('https://www.embaixadacarioca.com'+from+'?utm_source=test'),env:{ASSETS:noAssets},next(){throw Error('Redirect missing');}});
 assert.equal(direct.status,301);assert.equal(direct.headers.get('Location'),to+'?utm_source=test');
 assert.ok(!merged.some(([source])=>source===to),'redirect chain: '+to);
 const alias=await onRequest({request:new Request('https://www.embaixadacarioca.com'+from.replace(/\.html$/,'')),env:{ASSETS:noAssets},next(){throw Error('Alias redirect missing');}});
 assert.equal(alias.status,301);assert.equal(alias.headers.get('Location'),to);
}

console.log('Router regression checks: PASS (8 redirects, 3 stored pages, unknown 404, 9 revalidation cases, 404 page, 32 consolidated URLs).');
