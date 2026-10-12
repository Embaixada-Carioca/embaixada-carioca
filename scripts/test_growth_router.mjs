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
console.log('Router regression checks: PASS (8 redirects, 3 stored pages, unknown 404).');
