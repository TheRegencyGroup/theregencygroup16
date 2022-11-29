/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';
import Concurrency from 'web.concurrency';

const { Component, useState, onMounted, useRef } = owl;
const dropPrevious = new Concurrency.MutexedDropPrevious();

export class CustomerCommentInCart extends Component {
    setup() {
        onMounted(this.setSavedCommentAsInputValue.bind(this))
        this.actualSavedComment = this.props.comment;
        this.state = useState({
            hasActiveOrder: this.props.hasSaleOrder,
            processSaving: false,
            hasSavedComment: Boolean(this.props.comment),
            hasUnsavedChanges: false,
        });
    }

    setSavedCommentAsInputValue() {
        this.inputCommentTagRef.value = this.actualSavedComment || '';
    }

    get inputCommentTagRef() {
        return document.querySelector('.customer_comment_input')
    }

    async onClickSave() {
        let prevReadOnlyState = this.inputCommentTagRef.readOnly;
        this.inputCommentTagRef.readOnly = true;
        let prevComment = this.actualSavedComment;
        let customer_comment = this.inputCommentTagRef.value || '';
        this.actualSavedComment = customer_comment;
        this.state.processSaving = true;
        let isSuccessfullySaved = false;
        try {
            await rpc.query({
                route: '/shop/cart/submit_customer_comment',
                params: {
                    customer_comment
                },
            });
            this.state.hasUnsavedChanges = false;
            this.state.hasSavedComment = Boolean(customer_comment);
            isSuccessfullySaved = true;
        } catch (e) {
            this.state.hasUnsavedChanges = true;
            this.actualSavedComment = prevComment;
            alert(e.message?.data?.message || e.toString());
        }
        this.state.processSaving = false;
        this.inputCommentTagRef.readOnly = prevReadOnlyState;
        return isSuccessfullySaved
    }

    async onClickDelete() {
        let prevInputVal = this.inputCommentTagRef.value
        this.inputCommentTagRef.value = '';
        let isSuccessfullySaved = await this.onClickSave();
        if (!isSuccessfullySaved) {
            this.inputCommentTagRef.value = prevInputVal;
        }
    }

    async onCommentInput(ev) {
        this.state.hasUnsavedChanges = (ev.target.value !== this.actualSavedComment);
    }
}

CustomerCommentInCart.props = {
    comment: {
        type: String,
    },
    hasSaleOrder: {
        type: Boolean,
    },
}

CustomerCommentInCart.template = 'customer_comment_in_cart';

mountComponentAsWidget('CustomerCommentInCart', CustomerCommentInCart).catch();
