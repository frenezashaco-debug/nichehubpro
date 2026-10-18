const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'contact.js'),'utf8');
async function test(outcome){
 let submit,requests=0,resets=0;
 const nodes={
  'contact-form':{action:'https://formspree.io/f/mojyklpq',addEventListener(type,fn){submit=fn;},reset(){resets++;}},
  'contact-btn':{disabled:false,textContent:'Send Message'},'contact-success':{hidden:true},'contact-error':{hidden:true}
 };
 const context={document:{getElementById:id=>nodes[id]},FormData:class{},fetch:async(url,opts)=>{
  requests++; assert.equal(url,nodes['contact-form'].action); assert.equal(opts.method,'POST');
  if(outcome==='network')throw Error('offline'); return {ok:outcome==='accepted'};
 }};
 vm.runInNewContext(source,context);
 submit({preventDefault(){}});submit({preventDefault(){}});
 await new Promise(setImmediate);
 assert.equal(requests,1,'duplicate in-flight submission blocked');
 assert.equal(nodes['contact-success'].hidden,outcome!=='accepted');
 assert.equal(nodes['contact-error'].hidden,outcome==='accepted');
 assert.equal(resets,outcome==='accepted'?1:0);
 assert.equal(nodes['contact-btn'].disabled,false);
}
(async()=>{for(const outcome of ['accepted','rejected','network'])await test(outcome);console.log('PASS: contact acceptance, rejection, network error, retry state and duplicate-submit guard; no real submission sent.');})().catch(e=>{console.error(e);process.exitCode=1;});
