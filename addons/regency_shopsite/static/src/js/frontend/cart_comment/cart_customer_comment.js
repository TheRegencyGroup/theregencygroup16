/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const { Component, useState, onMounted, useRef } = owl;

export class CustomerCommentInCart extends Component {
    setup() {
        onMounted(this.setSavedCommentAsInputValue.bind(this))
        this.actualSavedComment = this.props.comment;
        this.state = useState({
            processSaving: false,
            hasSavedComment: Boolean(this.props.comment),
            hasUnsavedChanges: false,
        });

        this.commentInput = useRef('comment_input');
    }

    setSavedCommentAsInputValue() {
        this.commentInput.el.value = this.actualSavedComment || '';
    }

    async onClickSave() {
        let prevReadOnlyState = this.commentInput.el.readOnly;
        this.commentInput.el.readOnly = true;
        let prevComment = this.actualSavedComment;
        let customer_comment = this.commentInput.el.value || '';
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
        this.commentInput.el.readOnly = prevReadOnlyState;
        return isSuccessfullySaved;
    }

    async onClickDelete() {
        let prevInputVal = this.commentInput.el.value
        this.commentInput.el.value = '';
        let isSuccessfullySaved = await this.onClickSave();
        if (!isSuccessfullySaved) {
            this.commentInput.el.value = prevInputVal;
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
}

CustomerCommentInCart.template = 'customer_comment_in_cart';

mountComponentAsWidget('CustomerCommentInCart', CustomerCommentInCart).catch();
