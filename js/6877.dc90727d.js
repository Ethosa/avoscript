"use strict";(self["webpackChunkavoscript"]=self["webpackChunkavoscript"]||[]).push([[6877],{26877:function(e,t,i){i.r(t),i.d(t,{Adapter:function(){return y},CodeActionAdaptor:function(){return R},DefinitionAdapter:function(){return D},DiagnosticsAdapter:function(){return S},FormatAdapter:function(){return K},FormatHelper:function(){return N},FormatOnTypeAdapter:function(){return M},InlayHintsAdapter:function(){return H},Kind:function(){return L},LibFiles:function(){return w},OccurrencesAdapter:function(){return A},OutlineAdapter:function(){return I},QuickInfoAdapter:function(){return C},ReferenceAdapter:function(){return F},RenameAdapter:function(){return E},SignatureHelpAdapter:function(){return x},SuggestAdapter:function(){return v},WorkerManager:function(){return f},flattenDiagnosticMessageText:function(){return b},getJavaScriptWorker:function(){return j},getTypeScriptWorker:function(){return B},setupJavaScript:function(){return W},setupTypeScript:function(){return V}});var s=i(82482),n=(i(21703),i(92039)),r=i(22376),a=Object.defineProperty,o=Object.getOwnPropertyDescriptor,l=Object.getOwnPropertyNames,c=Object.prototype.hasOwnProperty,u=(e,t,i)=>t in e?a(e,t,{enumerable:!0,configurable:!0,writable:!0,value:i}):e[t]=i,d=(e,t,i,s)=>{if(t&&"object"===typeof t||"function"===typeof t)for(let n of l(t))c.call(e,n)||n===i||a(e,n,{get:()=>t[n],enumerable:!(s=o(t,n))||s.enumerable});return e},g=(e,t,i)=>(d(e,t,"default"),i&&d(i,t,"default")),p=(e,t,i)=>(u(e,"symbol"!==typeof t?t+"":t,i),i),m={};g(m,n);var f=class{constructor(e,t){(0,s.Z)(this,"_configChangeListener",void 0),(0,s.Z)(this,"_updateExtraLibsToken",void 0),(0,s.Z)(this,"_extraLibsChangeListener",void 0),(0,s.Z)(this,"_worker",void 0),(0,s.Z)(this,"_client",void 0),this._modeId=e,this._defaults=t,this._worker=null,this._client=null,this._configChangeListener=this._defaults.onDidChange((()=>this._stopWorker())),this._updateExtraLibsToken=0,this._extraLibsChangeListener=this._defaults.onDidExtraLibsChange((()=>this._updateExtraLibs()))}dispose(){this._configChangeListener.dispose(),this._extraLibsChangeListener.dispose(),this._stopWorker()}_stopWorker(){this._worker&&(this._worker.dispose(),this._worker=null),this._client=null}async _updateExtraLibs(){if(!this._worker)return;const e=++this._updateExtraLibsToken,t=await this._worker.getProxy();this._updateExtraLibsToken===e&&t.updateExtraLibs(this._defaults.getExtraLibs())}_getClient(){return this._client||(this._client=(async()=>(this._worker=m.editor.createWebWorker({moduleId:"vs/language/typescript/tsWorker",label:this._modeId,keepIdleModels:!0,createData:{compilerOptions:this._defaults.getCompilerOptions(),extraLibs:this._defaults.getExtraLibs(),customWorkerPath:this._defaults.workerOptions.customWorkerPath,inlayHintsOptions:this._defaults.inlayHintsOptions}}),this._defaults.getEagerModelSync()?await this._worker.withSyncedResources(m.editor.getModels().filter((e=>e.getLanguageId()===this._modeId)).map((e=>e.uri))):await this._worker.getProxy()))()),this._client}async getLanguageServiceWorker(...e){const t=await this._getClient();return this._worker&&await this._worker.withSyncedResources(e),t}},h={};function b(e,t,i=0){if("string"===typeof e)return e;if(void 0===e)return"";let s="";if(i){s+=t;for(let e=0;e<i;e++)s+="  "}if(s+=e.messageText,i++,e.next)for(const n of e.next)s+=b(n,t,i);return s}function _(e){return e?e.map((e=>e.text)).join(""):""}h["lib.d.ts"]=!0,h["lib.dom.d.ts"]=!0,h["lib.dom.iterable.d.ts"]=!0,h["lib.es2015.collection.d.ts"]=!0,h["lib.es2015.core.d.ts"]=!0,h["lib.es2015.d.ts"]=!0,h["lib.es2015.generator.d.ts"]=!0,h["lib.es2015.iterable.d.ts"]=!0,h["lib.es2015.promise.d.ts"]=!0,h["lib.es2015.proxy.d.ts"]=!0,h["lib.es2015.reflect.d.ts"]=!0,h["lib.es2015.symbol.d.ts"]=!0,h["lib.es2015.symbol.wellknown.d.ts"]=!0,h["lib.es2016.array.include.d.ts"]=!0,h["lib.es2016.d.ts"]=!0,h["lib.es2016.full.d.ts"]=!0,h["lib.es2017.d.ts"]=!0,h["lib.es2017.full.d.ts"]=!0,h["lib.es2017.intl.d.ts"]=!0,h["lib.es2017.object.d.ts"]=!0,h["lib.es2017.sharedmemory.d.ts"]=!0,h["lib.es2017.string.d.ts"]=!0,h["lib.es2017.typedarrays.d.ts"]=!0,h["lib.es2018.asyncgenerator.d.ts"]=!0,h["lib.es2018.asynciterable.d.ts"]=!0,h["lib.es2018.d.ts"]=!0,h["lib.es2018.full.d.ts"]=!0,h["lib.es2018.intl.d.ts"]=!0,h["lib.es2018.promise.d.ts"]=!0,h["lib.es2018.regexp.d.ts"]=!0,h["lib.es2019.array.d.ts"]=!0,h["lib.es2019.d.ts"]=!0,h["lib.es2019.full.d.ts"]=!0,h["lib.es2019.object.d.ts"]=!0,h["lib.es2019.string.d.ts"]=!0,h["lib.es2019.symbol.d.ts"]=!0,h["lib.es2020.bigint.d.ts"]=!0,h["lib.es2020.d.ts"]=!0,h["lib.es2020.full.d.ts"]=!0,h["lib.es2020.intl.d.ts"]=!0,h["lib.es2020.promise.d.ts"]=!0,h["lib.es2020.sharedmemory.d.ts"]=!0,h["lib.es2020.string.d.ts"]=!0,h["lib.es2020.symbol.wellknown.d.ts"]=!0,h["lib.es2021.d.ts"]=!0,h["lib.es2021.full.d.ts"]=!0,h["lib.es2021.intl.d.ts"]=!0,h["lib.es2021.promise.d.ts"]=!0,h["lib.es2021.string.d.ts"]=!0,h["lib.es2021.weakref.d.ts"]=!0,h["lib.es5.d.ts"]=!0,h["lib.es6.d.ts"]=!0,h["lib.esnext.d.ts"]=!0,h["lib.esnext.full.d.ts"]=!0,h["lib.esnext.intl.d.ts"]=!0,h["lib.esnext.promise.d.ts"]=!0,h["lib.esnext.string.d.ts"]=!0,h["lib.esnext.weakref.d.ts"]=!0,h["lib.scripthost.d.ts"]=!0,h["lib.webworker.d.ts"]=!0,h["lib.webworker.importscripts.d.ts"]=!0,h["lib.webworker.iterable.d.ts"]=!0;var y=class{constructor(e){this._worker=e}_textSpanToRange(e,t){let i=e.getPositionAt(t.start),s=e.getPositionAt(t.start+t.length),{lineNumber:n,column:r}=i,{lineNumber:a,column:o}=s;return{startLineNumber:n,startColumn:r,endLineNumber:a,endColumn:o}}},w=class{constructor(e){(0,s.Z)(this,"_libFiles",void 0),(0,s.Z)(this,"_hasFetchedLibFiles",void 0),(0,s.Z)(this,"_fetchLibFilesPromise",void 0),this._worker=e,this._libFiles={},this._hasFetchedLibFiles=!1,this._fetchLibFilesPromise=null}isLibFile(e){return!!e&&(0===e.path.indexOf("/lib.")&&!!h[e.path.slice(1)])}getOrCreateModel(e){const t=m.Uri.parse(e),i=m.editor.getModel(t);if(i)return i;if(this.isLibFile(t)&&this._hasFetchedLibFiles)return m.editor.createModel(this._libFiles[t.path.slice(1)],"typescript",t);const s=r.typescriptDefaults.getExtraLibs()[e];return s?m.editor.createModel(s.content,"typescript",t):null}_containsLibFile(e){for(let t of e)if(this.isLibFile(t))return!0;return!1}async fetchLibFilesIfNecessary(e){this._containsLibFile(e)&&await this._fetchLibFiles()}_fetchLibFiles(){return this._fetchLibFilesPromise||(this._fetchLibFilesPromise=this._worker().then((e=>e.getLibFiles())).then((e=>{this._hasFetchedLibFiles=!0,this._libFiles=e}))),this._fetchLibFilesPromise}},S=class extends y{constructor(e,t,i,n){super(n),(0,s.Z)(this,"_disposables",[]),(0,s.Z)(this,"_listener",Object.create(null)),this._libFiles=e,this._defaults=t,this._selector=i;const r=e=>{if(e.getLanguageId()!==i)return;const t=()=>{const{onlyVisible:t}=this._defaults.getDiagnosticsOptions();t?e.isAttachedToEditor()&&this._doValidate(e):this._doValidate(e)};let s;const n=e.onDidChangeContent((()=>{clearTimeout(s),s=window.setTimeout(t,500)})),r=e.onDidChangeAttached((()=>{const{onlyVisible:i}=this._defaults.getDiagnosticsOptions();i&&(e.isAttachedToEditor()?t():m.editor.setModelMarkers(e,this._selector,[]))}));this._listener[e.uri.toString()]={dispose(){n.dispose(),r.dispose(),clearTimeout(s)}},t()},a=e=>{m.editor.setModelMarkers(e,this._selector,[]);const t=e.uri.toString();this._listener[t]&&(this._listener[t].dispose(),delete this._listener[t])};this._disposables.push(m.editor.onDidCreateModel((e=>r(e)))),this._disposables.push(m.editor.onWillDisposeModel(a)),this._disposables.push(m.editor.onDidChangeModelLanguage((e=>{a(e.model),r(e.model)}))),this._disposables.push({dispose(){for(const e of m.editor.getModels())a(e)}});const o=()=>{for(const e of m.editor.getModels())a(e),r(e)};this._disposables.push(this._defaults.onDidChange(o)),this._disposables.push(this._defaults.onDidExtraLibsChange(o)),m.editor.getModels().forEach((e=>r(e)))}dispose(){this._disposables.forEach((e=>e&&e.dispose())),this._disposables=[]}async _doValidate(e){const t=await this._worker(e.uri);if(e.isDisposed())return;const i=[],{noSyntaxValidation:s,noSemanticValidation:n,noSuggestionDiagnostics:r}=this._defaults.getDiagnosticsOptions();s||i.push(t.getSyntacticDiagnostics(e.uri.toString())),n||i.push(t.getSemanticDiagnostics(e.uri.toString())),r||i.push(t.getSuggestionDiagnostics(e.uri.toString()));const a=await Promise.all(i);if(!a||e.isDisposed())return;const o=a.reduce(((e,t)=>t.concat(e)),[]).filter((e=>-1===(this._defaults.getDiagnosticsOptions().diagnosticCodesToIgnore||[]).indexOf(e.code))),l=o.map((e=>e.relatedInformation||[])).reduce(((e,t)=>t.concat(e)),[]).map((e=>e.file?m.Uri.parse(e.file.fileName):null));await this._libFiles.fetchLibFilesIfNecessary(l),e.isDisposed()||m.editor.setModelMarkers(e,this._selector,o.map((t=>this._convertDiagnostics(e,t))))}_convertDiagnostics(e,t){const i=t.start||0,s=t.length||1,{lineNumber:n,column:r}=e.getPositionAt(i),{lineNumber:a,column:o}=e.getPositionAt(i+s),l=[];return t.reportsUnnecessary&&l.push(m.MarkerTag.Unnecessary),t.reportsDeprecated&&l.push(m.MarkerTag.Deprecated),{severity:this._tsDiagnosticCategoryToMarkerSeverity(t.category),startLineNumber:n,startColumn:r,endLineNumber:a,endColumn:o,message:b(t.messageText,"\n"),code:t.code.toString(),tags:l,relatedInformation:this._convertRelatedInformation(e,t.relatedInformation)}}_convertRelatedInformation(e,t){if(!t)return[];const i=[];return t.forEach((t=>{let s=e;if(t.file&&(s=this._libFiles.getOrCreateModel(t.file.fileName)),!s)return;const n=t.start||0,r=t.length||1,{lineNumber:a,column:o}=s.getPositionAt(n),{lineNumber:l,column:c}=s.getPositionAt(n+r);i.push({resource:s.uri,startLineNumber:a,startColumn:o,endLineNumber:l,endColumn:c,message:b(t.messageText,"\n")})})),i}_tsDiagnosticCategoryToMarkerSeverity(e){switch(e){case 1:return m.MarkerSeverity.Error;case 3:return m.MarkerSeverity.Info;case 0:return m.MarkerSeverity.Warning;case 2:return m.MarkerSeverity.Hint}return m.MarkerSeverity.Info}},v=class extends y{get triggerCharacters(){return["."]}async provideCompletionItems(e,t,i,s){const n=e.getWordUntilPosition(t),r=new m.Range(t.lineNumber,n.startColumn,t.lineNumber,n.endColumn),a=e.uri,o=e.getOffsetAt(t),l=await this._worker(a);if(e.isDisposed())return;const c=await l.getCompletionsAtPosition(a.toString(),o);if(!c||e.isDisposed())return;const u=c.entries.map((i=>{let s=r;if(i.replacementSpan){const t=e.getPositionAt(i.replacementSpan.start),n=e.getPositionAt(i.replacementSpan.start+i.replacementSpan.length);s=new m.Range(t.lineNumber,t.column,n.lineNumber,n.column)}const n=[];return-1!==i.kindModifiers?.indexOf("deprecated")&&n.push(m.languages.CompletionItemTag.Deprecated),{uri:a,position:t,offset:o,range:s,label:i.name,insertText:i.name,sortText:i.sortText,kind:v.convertKind(i.kind),tags:n}}));return{suggestions:u}}async resolveCompletionItem(e,t){const i=e,s=i.uri,n=i.position,r=i.offset,a=await this._worker(s),o=await a.getCompletionEntryDetails(s.toString(),r,i.label);return o?{uri:s,position:n,label:o.name,kind:v.convertKind(o.kind),detail:_(o.displayParts),documentation:{value:v.createDocumentationString(o)}}:i}static convertKind(e){switch(e){case L.primitiveType:case L.keyword:return m.languages.CompletionItemKind.Keyword;case L.variable:case L.localVariable:return m.languages.CompletionItemKind.Variable;case L.memberVariable:case L.memberGetAccessor:case L.memberSetAccessor:return m.languages.CompletionItemKind.Field;case L.function:case L.memberFunction:case L.constructSignature:case L.callSignature:case L.indexSignature:return m.languages.CompletionItemKind.Function;case L.enum:return m.languages.CompletionItemKind.Enum;case L.module:return m.languages.CompletionItemKind.Module;case L.class:return m.languages.CompletionItemKind.Class;case L.interface:return m.languages.CompletionItemKind.Interface;case L.warning:return m.languages.CompletionItemKind.File}return m.languages.CompletionItemKind.Property}static createDocumentationString(e){let t=_(e.documentation);if(e.tags)for(const i of e.tags)t+=`\n\n${k(i)}`;return t}};function k(e){let t=`*@${e.name}*`;if("param"===e.name&&e.text){const[i,...s]=e.text;t+=`\`${i.text}\``,s.length>0&&(t+=` — ${s.map((e=>e.text)).join(" ")}`)}else Array.isArray(e.text)?t+=` — ${e.text.map((e=>e.text)).join(" ")}`:e.text&&(t+=` — ${e.text}`);return t}var x=class e extends y{constructor(...e){super(...e),(0,s.Z)(this,"signatureHelpTriggerCharacters",["(",","])}static _toSignatureHelpTriggerReason(e){switch(e.triggerKind){case m.languages.SignatureHelpTriggerKind.TriggerCharacter:return e.triggerCharacter?e.isRetrigger?{kind:"retrigger",triggerCharacter:e.triggerCharacter}:{kind:"characterTyped",triggerCharacter:e.triggerCharacter}:{kind:"invoked"};case m.languages.SignatureHelpTriggerKind.ContentChange:return e.isRetrigger?{kind:"retrigger"}:{kind:"invoked"};case m.languages.SignatureHelpTriggerKind.Invoke:default:return{kind:"invoked"}}}async provideSignatureHelp(t,i,s,n){const r=t.uri,a=t.getOffsetAt(i),o=await this._worker(r);if(t.isDisposed())return;const l=await o.getSignatureHelpItems(r.toString(),a,{triggerReason:e._toSignatureHelpTriggerReason(n)});if(!l||t.isDisposed())return;const c={activeSignature:l.selectedItemIndex,activeParameter:l.argumentIndex,signatures:[]};return l.items.forEach((e=>{const t={label:"",parameters:[]};t.documentation={value:_(e.documentation)},t.label+=_(e.prefixDisplayParts),e.parameters.forEach(((i,s,n)=>{const r=_(i.displayParts),a={label:r,documentation:{value:_(i.documentation)}};t.label+=r,t.parameters.push(a),s<n.length-1&&(t.label+=_(e.separatorDisplayParts))})),t.label+=_(e.suffixDisplayParts),c.signatures.push(t)})),{value:c,dispose(){}}}},C=class extends y{async provideHover(e,t,i){const s=e.uri,n=e.getOffsetAt(t),r=await this._worker(s);if(e.isDisposed())return;const a=await r.getQuickInfoAtPosition(s.toString(),n);if(!a||e.isDisposed())return;const o=_(a.documentation),l=a.tags?a.tags.map((e=>k(e))).join("  \n\n"):"",c=_(a.displayParts);return{range:this._textSpanToRange(e,a.textSpan),contents:[{value:"```typescript\n"+c+"\n```\n"},{value:o+(l?"\n\n"+l:"")}]}}},A=class extends y{async provideDocumentHighlights(e,t,i){const s=e.uri,n=e.getOffsetAt(t),r=await this._worker(s);if(e.isDisposed())return;const a=await r.getOccurrencesAtPosition(s.toString(),n);return a&&!e.isDisposed()?a.map((t=>({range:this._textSpanToRange(e,t.textSpan),kind:t.isWriteAccess?m.languages.DocumentHighlightKind.Write:m.languages.DocumentHighlightKind.Text}))):void 0}},D=class extends y{constructor(e,t){super(t),this._libFiles=e}async provideDefinition(e,t,i){const s=e.uri,n=e.getOffsetAt(t),r=await this._worker(s);if(e.isDisposed())return;const a=await r.getDefinitionAtPosition(s.toString(),n);if(!a||e.isDisposed())return;if(await this._libFiles.fetchLibFilesIfNecessary(a.map((e=>m.Uri.parse(e.fileName)))),e.isDisposed())return;const o=[];for(let l of a){const e=this._libFiles.getOrCreateModel(l.fileName);e&&o.push({uri:e.uri,range:this._textSpanToRange(e,l.textSpan)})}return o}},F=class extends y{constructor(e,t){super(t),this._libFiles=e}async provideReferences(e,t,i,s){const n=e.uri,r=e.getOffsetAt(t),a=await this._worker(n);if(e.isDisposed())return;const o=await a.getReferencesAtPosition(n.toString(),r);if(!o||e.isDisposed())return;if(await this._libFiles.fetchLibFilesIfNecessary(o.map((e=>m.Uri.parse(e.fileName)))),e.isDisposed())return;const l=[];for(let c of o){const e=this._libFiles.getOrCreateModel(c.fileName);e&&l.push({uri:e.uri,range:this._textSpanToRange(e,c.textSpan)})}return l}},I=class extends y{async provideDocumentSymbols(e,t){const i=e.uri,s=await this._worker(i);if(e.isDisposed())return;const n=await s.getNavigationBarItems(i.toString());if(!n||e.isDisposed())return;const r=(t,i,s)=>{let n={name:i.text,detail:"",kind:T[i.kind]||m.languages.SymbolKind.Variable,range:this._textSpanToRange(e,i.spans[0]),selectionRange:this._textSpanToRange(e,i.spans[0]),tags:[]};if(s&&(n.containerName=s),i.childItems&&i.childItems.length>0)for(let e of i.childItems)r(t,e,n.name);t.push(n)};let a=[];return n.forEach((e=>r(a,e))),a}},L=class{};p(L,"unknown",""),p(L,"keyword","keyword"),p(L,"script","script"),p(L,"module","module"),p(L,"class","class"),p(L,"interface","interface"),p(L,"type","type"),p(L,"enum","enum"),p(L,"variable","var"),p(L,"localVariable","local var"),p(L,"function","function"),p(L,"localFunction","local function"),p(L,"memberFunction","method"),p(L,"memberGetAccessor","getter"),p(L,"memberSetAccessor","setter"),p(L,"memberVariable","property"),p(L,"constructorImplementation","constructor"),p(L,"callSignature","call"),p(L,"indexSignature","index"),p(L,"constructSignature","construct"),p(L,"parameter","parameter"),p(L,"typeParameter","type parameter"),p(L,"primitiveType","primitive type"),p(L,"label","label"),p(L,"alias","alias"),p(L,"const","const"),p(L,"let","let"),p(L,"warning","warning");var T=Object.create(null);T[L.module]=m.languages.SymbolKind.Module,T[L.class]=m.languages.SymbolKind.Class,T[L.enum]=m.languages.SymbolKind.Enum,T[L.interface]=m.languages.SymbolKind.Interface,T[L.memberFunction]=m.languages.SymbolKind.Method,T[L.memberVariable]=m.languages.SymbolKind.Property,T[L.memberGetAccessor]=m.languages.SymbolKind.Property,T[L.memberSetAccessor]=m.languages.SymbolKind.Property,T[L.variable]=m.languages.SymbolKind.Variable,T[L.const]=m.languages.SymbolKind.Variable,T[L.localVariable]=m.languages.SymbolKind.Variable,T[L.variable]=m.languages.SymbolKind.Variable,T[L.function]=m.languages.SymbolKind.Function,T[L.localFunction]=m.languages.SymbolKind.Function;var P,O,N=class extends y{static _convertOptions(e){return{ConvertTabsToSpaces:e.insertSpaces,TabSize:e.tabSize,IndentSize:e.tabSize,IndentStyle:2,NewLineCharacter:"\n",InsertSpaceAfterCommaDelimiter:!0,InsertSpaceAfterSemicolonInForStatements:!0,InsertSpaceBeforeAndAfterBinaryOperators:!0,InsertSpaceAfterKeywordsInControlFlowStatements:!0,InsertSpaceAfterFunctionKeywordForAnonymousFunctions:!0,InsertSpaceAfterOpeningAndBeforeClosingNonemptyParenthesis:!1,InsertSpaceAfterOpeningAndBeforeClosingNonemptyBrackets:!1,InsertSpaceAfterOpeningAndBeforeClosingTemplateStringBraces:!1,PlaceOpenBraceOnNewLineForControlBlocks:!1,PlaceOpenBraceOnNewLineForFunctions:!1}}_convertTextChanges(e,t){return{text:t.newText,range:this._textSpanToRange(e,t.span)}}},K=class extends N{async provideDocumentRangeFormattingEdits(e,t,i,s){const n=e.uri,r=e.getOffsetAt({lineNumber:t.startLineNumber,column:t.startColumn}),a=e.getOffsetAt({lineNumber:t.endLineNumber,column:t.endColumn}),o=await this._worker(n);if(e.isDisposed())return;const l=await o.getFormattingEditsForRange(n.toString(),r,a,N._convertOptions(i));return l&&!e.isDisposed()?l.map((t=>this._convertTextChanges(e,t))):void 0}},M=class extends N{get autoFormatTriggerCharacters(){return[";","}","\n"]}async provideOnTypeFormattingEdits(e,t,i,s,n){const r=e.uri,a=e.getOffsetAt(t),o=await this._worker(r);if(e.isDisposed())return;const l=await o.getFormattingEditsAfterKeystroke(r.toString(),a,i,N._convertOptions(s));return l&&!e.isDisposed()?l.map((t=>this._convertTextChanges(e,t))):void 0}},R=class extends N{async provideCodeActions(e,t,i,s){const n=e.uri,r=e.getOffsetAt({lineNumber:t.startLineNumber,column:t.startColumn}),a=e.getOffsetAt({lineNumber:t.endLineNumber,column:t.endColumn}),o=N._convertOptions(e.getOptions()),l=i.markers.filter((e=>e.code)).map((e=>e.code)).map(Number),c=await this._worker(n);if(e.isDisposed())return;const u=await c.getCodeFixesAtPosition(n.toString(),r,a,l,o);if(!u||e.isDisposed())return{actions:[],dispose:()=>{}};const d=u.filter((e=>0===e.changes.filter((e=>e.isNewFile)).length)).map((t=>this._tsCodeFixActionToMonacoCodeAction(e,i,t)));return{actions:d,dispose:()=>{}}}_tsCodeFixActionToMonacoCodeAction(e,t,i){const s=[];for(const r of i.changes)for(const t of r.textChanges)s.push({resource:e.uri,versionId:void 0,textEdit:{range:this._textSpanToRange(e,t.span),text:t.newText}});const n={title:i.description,edit:{edits:s},diagnostics:t.markers,kind:"quickfix"};return n}},E=class extends y{constructor(e,t){super(t),this._libFiles=e}async provideRenameEdits(e,t,i,s){const n=e.uri,r=n.toString(),a=e.getOffsetAt(t),o=await this._worker(n);if(e.isDisposed())return;const l=await o.getRenameInfo(r,a,{allowRenameOfImportPath:!1});if(!1===l.canRename)return{edits:[],rejectReason:l.localizedErrorMessage};if(void 0!==l.fileToRename)throw new Error("Renaming files is not supported.");const c=await o.findRenameLocations(r,a,!1,!1,!1);if(!c||e.isDisposed())return;const u=[];for(const d of c){const e=this._libFiles.getOrCreateModel(d.fileName);if(!e)throw new Error(`Unknown file ${d.fileName}.`);u.push({resource:e.uri,versionId:void 0,textEdit:{range:this._textSpanToRange(e,d.textSpan),text:i}})}return{edits:u}}},H=class extends y{async provideInlayHints(e,t,i){const s=e.uri,n=s.toString(),r=e.getOffsetAt({lineNumber:t.startLineNumber,column:t.startColumn}),a=e.getOffsetAt({lineNumber:t.endLineNumber,column:t.endColumn}),o=await this._worker(s);if(e.isDisposed())return null;const l=await o.provideInlayHints(n,r,a),c=l.map((t=>({...t,label:t.text,position:e.getPositionAt(t.position),kind:this._convertHintKind(t.kind)})));return{hints:c,dispose:()=>{}}}_convertHintKind(e){switch(e){case"Parameter":return m.languages.InlayHintKind.Parameter;case"Type":return m.languages.InlayHintKind.Type;default:return m.languages.InlayHintKind.Type}}};function V(e){O=Z(e,"typescript")}function W(e){P=Z(e,"javascript")}function j(){return new Promise(((e,t)=>{if(!P)return t("JavaScript not registered!");e(P)}))}function B(){return new Promise(((e,t)=>{if(!O)return t("TypeScript not registered!");e(O)}))}function Z(e,t){const i=new f(t,e),s=(...e)=>i.getLanguageServiceWorker(...e),n=new w(s);return m.languages.registerCompletionItemProvider(t,new v(s)),m.languages.registerSignatureHelpProvider(t,new x(s)),m.languages.registerHoverProvider(t,new C(s)),m.languages.registerDocumentHighlightProvider(t,new A(s)),m.languages.registerDefinitionProvider(t,new D(n,s)),m.languages.registerReferenceProvider(t,new F(n,s)),m.languages.registerDocumentSymbolProvider(t,new I(s)),m.languages.registerDocumentRangeFormattingEditProvider(t,new K(s)),m.languages.registerOnTypeFormattingEditProvider(t,new M(s)),m.languages.registerCodeActionProvider(t,new R(s)),m.languages.registerRenameProvider(t,new E(n,s)),m.languages.registerInlayHintsProvider(t,new H(s)),new S(n,e,t,s),s}}}]);
//# sourceMappingURL=6877.dc90727d.js.map