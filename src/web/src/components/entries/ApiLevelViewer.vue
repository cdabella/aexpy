<script setup lang="ts">
import { NTree, NInput, NFlex, TreeOption, NButton } from 'naive-ui';
import { computed, h, onMounted, ref, watch } from 'vue';
import ApiEntryLink from '../links/ApiEntryLink.vue';
import ApiEntryTypeTag from '../metadata/ApiEntryTypeTag.vue';
import ApiEntryMetadataTag from '../metadata/ApiEntryMetadataTag.vue';
import { ApiDescription } from '../../models'
import { ApiEntry, FunctionEntry } from '../../models/description';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import { hashedColor, apiUrl } from '../../services/utils';
import { buildApiTreeOptions } from '../../services/ui';
import { Api } from '@vicons/tabler';

const props = defineProps<{
    api: ApiDescription,
    current?: ApiEntry,
    pattern?: string,
    entryUrl?: string,
}>();

const data = computed(() => buildApiTreeOptions(props.api, props.entryUrl));

const defaultExpandedKeys = computed(() => {
    if (!props.current) {
        return [];
    }
    let parts = props.current.id.split(".");
    let result = [];
    let current = "";
    for (let part of parts) {
        if (current == "") {
            current = part;
        } else {
            current += `.${part}`;
        }
        result.push(current);
    }
    return result;
})
</script>

<template>
    <n-tree :pattern="props.pattern" :data="data" block-line :default-expanded-keys="defaultExpandedKeys"
        :show-irrelevant-nodes="false" />
</template>