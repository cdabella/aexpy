<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui'
import { DescriptionIcon } from '../icons'
import { apiUrl } from '../../services/utils'
import { Release } from '../../models';

defineProps<{
    release: Release
}>();

</script>

<template>
    <router-link :to="apiUrl(release)" custom v-slot="{ href, navigate }">
        <n-button tag="a" :href="href" @click="navigate" type="info" ghost>
            <n-icon size="large" :component="DescriptionIcon" />
        </n-button>
    </router-link>
</template>