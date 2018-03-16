/**
 * @license
 * Copyright 2017 The Tensor2Tensor Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * 
 *
 * ### Usage
 *
 *   <corpus-search-view></corpus-search-view>
 */
class CorpusSearchView extends Polymer.Element {
  /**
   * @return {string} The component name.
   */
  static get is() {
    return 'corpus-search-view';
  }

  /**
   * @return {!Object} The component properties.
   */
  static get properties() {
    return {
      route: {
        type: Object,
      },

      query_: {
        type: Object,
      },

      result_: {
        type: Object,
      }
    };
  }


  createBodyValue_(params) {
    // Add the key value body parts.
    var bodyParts = [];
    for (var param in params) {
      var value = window.encodeURIComponent(params[param]);
      // console.log(value)
      bodyParts.push(param + "=" + value);
    }

    // Combine everything together.
    return bodyParts.join('&');
  }

  process_index_query_() {
    console.log("process_index_query_: query="+window.encodeURIComponent(this.query_));

    this.set('url', '/api/corpussearch?query='+window.encodeURIComponent(this.query_));
    this.set('displayResult', false);
    this.$.translateAjax.generateRequest();
  }

  clear_index_(){
   console.log("Clearing index")
    this.set('url', '/api/cleartensorindex');
    this.$.translateAjax.generateRequest();

  }

  process_neuralnet_index_query_(){
    console.log("process_neuralnet_index_query_: query="+window.encodeURIComponent(this.nnquery_));

    var params = {
      'query': this.nnquery_,
      'id': this.model_.id,
      'sl': this.model_.source_language.code,
      'tl': this.model_.target_language.code,
    };
    
    var paramList = this.createBodyValue_(params)

    this.set('url', '/api/nncorpussearch?'+ paramList);
    this.set('displayResult', false);
    this.$.translateAjax.generateRequest();
  

  }

  handleQueryResponse_(event) {

    console.log("AJAX response: " + event.detail.response);
    console.log("query_: " + this.query_);

    this.set('result_', {
      response: event.detail.response,
      query: this.query_,
    });
    this.set('displayResult', true);

    console.log(this.result_.response);

}

  ready() {
    super.ready();
    if (typeof this.result_ === 'undefined' || this.result_ === null)
      this.set('displayResult', false);
    else
      this.set('displayResult', true);
  }  

  /**
   * Noop
   * @public
   */
  refresh() {
    console.log("corpus-search-view: refresh()");
    this.set('result_', null);
    this.set('displayResult', false);
  }
}

customElements.define(CorpusSearchView.is, CorpusSearchView);
