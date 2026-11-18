const fs=require('fs'),vm=require('vm'),assert=require('assert');
async function check(file,errName,expected){
 const nodes={};const listeners={};let calls=0;
 const ids=file.includes('biometric')?['biometric-app','camera-preview','start-camera','start-enrollment','challenge-panel','challenge-text','challenge-progress','camera-status']:['punch-app','video','start-camera','start-verification','challenge-panel','challenge-text','challenge-countdown','status','elapsed-time','tipo'];
 for(const id of ids)nodes[id]={dataset:{},textContent:'',disabled:false,classList:{add(){},remove(){},toggle(){}},addEventListener(event,cb){listeners[id+':'+event]=cb}};
 let release;const media={getUserMedia(){calls++;return new Promise((_,reject)=>{release=()=>reject(Object.assign(new Error(),{name:errName}))})}};
 const window={isSecureContext:true,addEventListener(){},setTimeout,clearInterval,setInterval};
 vm.runInNewContext(fs.readFileSync(file,'utf8'),{document:{getElementById:id=>nodes[id]},window,navigator:{mediaDevices:media},console:{error(){}},performance,Promise,Error});
 assert.equal(calls,0,'camera must wait for user');let first=listeners['start-camera:click']();let second=listeners['start-camera:click']();assert.equal(calls,1,'concurrent attempts blocked');release();await Promise.all([first,second]);assert(nodes[file.includes('biometric')?'camera-status':'status'].textContent.includes(expected));assert.equal(nodes['start-camera'].disabled,false);
}
(async()=>{for(const f of ['static/punch.js','static/biometric_capture.js'])for(const [n,m] of [['NotReadableError','ocupada'],['NotAllowedError','Permissão'],['NotFoundError','Nenhuma câmera']])await check(f,n,m);console.log('6 cenários de câmera aprovados');})().catch(e=>{console.error(e);process.exit(1)});
