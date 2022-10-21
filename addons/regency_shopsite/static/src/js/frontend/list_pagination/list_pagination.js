/** @odoo-module **/
import "./store";
import { CHANGE_PAGE } from './store.js';

const { Component, useState } = owl;
const FIRST_PAGE = 1
import { useStore } from "@fe_owl_base/js/main";

export class ListPaginationComponent extends Component {
    setup() {
        this.store = useStore();
        this.list = this.store.catalogList.data;
        this.count = this.store.catalogList.count;
        this.limit = this.store.catalogList.limit;
        this.currentPage = this.store.catalogList.page;
        this.numberOfPages = this.calcNumberOfPages();
        this.updateList = this.store.catalogList.updateShopsiteCatalogList;

    }

    get isFirstCurrentPage(){
        return this.currentPage === FIRST_PAGE
    }
    get isLastCurrentPage(){
        return this.currentPage === this.numberOfPages
    }

    onClickPageBtn(pageNumber, event) {
        let isNotOutOfRange = pageNumber > 0 || pageNumber <= this.numberOfPages
        if (isNotOutOfRange) {
            this.changePage(pageNumber, () => {
                scrollListToTop();
            })
        }
    }

    calcNumberOfPages() {
        let listCount = this.count;
        let listLimit = this.limit;
        let numbers = Math.floor(listCount / listLimit);
        if (listCount % listLimit > 0) {
            numbers++;
        }
        return numbers;
    }

    leftPages() {
        let pages = [1];
        if (this.store.currentPage <= this.props.pageOffset * 2) {
            pages = this.arrayFromRange(1, this.store.currentPage + this.props.pageOffset);
        }
        return pages;
    }

    centerPages() {
        let pages = false;
        if (this.store.currentPage > this.props.pageOffset * 2 && this.store.currentPage <= this.store.numberOfPages - this.props.pageOffset * 2) {
            pages = this.arrayFromRange(this.store.currentPage - this.props.pageOffset, this.store.currentPage + this.props.pageOffset);
        }
        return pages;
    }

    rightPages() {
        let pages = [this.store.numberOfPages];
        if (this.store.currentPage > this.store.numberOfPages - this.props.pageOffset * 2) {
            pages = this.arrayFromRange(this.store.currentPage - this.props.pageOffset, this.store.numberOfPages);
        }
        return pages;
    }

    arrayFromRange(min, max) {
        return Array.from({ length: max - min + 1 }, (a, e) => e + min);
    }

    async changePage(pageNumber, callback) {
        await this.updateList(pageNumber);
        if (callback) {
            callback();
        }
    }
}

ListPaginationComponent.defaultProps = {
    pageOffset: 2,
    localPagination: false,
}
ListPaginationComponent.props = {
    listKey: {
        type: String,
    },
    pageOffset: {
        type: Number,
    },
    localPagination: {
        type: Boolean,
    },
}

ListPaginationComponent.template = 'list_pagination';

function scrollListToTop () {
    let list = document.querySelector('#wrap');
    if (list) {
        list.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
}

export {
    scrollListToTop
}
