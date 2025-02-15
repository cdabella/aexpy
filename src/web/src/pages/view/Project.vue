<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NPageHeader, NFlex, NSpace, NText, NBreadcrumb, NCollapseTransition, NDivider, NDrawer, NDrawerContent, NProgress, NBreadcrumbItem, NSwitch, NCollapse, useLoadingBar, NCollapseItem, NLog, NIcon, NLayoutContent, NAvatar, NStatistic, NTabs, NTabPane, NCard, NButton, useOsTheme, useMessage, NDescriptions, NDescriptionsItem, NSpin } from 'naive-ui'
import { HomeIcon, RootIcon, DataIcon, TrendIcon, CountIcon, PackageIcon, LogIcon, PreprocessIcon, VersionIcon, DiffIcon, ExtractIcon, EvaluateIcon, ReportIcon } from '../../components/icons'
import { useRouter, useRoute } from 'vue-router'
import HomeBreadcrumbItem from '../../components/breadcrumbs/HomeBreadcrumbItem.vue'
import { useStore } from '../../services/store'
import { Distribution, Release, ApiDescription, ApiDifference, Report, ReleasePair, ProduceState, PackageProductIndex } from '../../models'
import { numberSum, numberAverage, publicVars, apiUrl, changeUrl, distributionUrl, reportUrl, hashedColor } from '../../services/utils'
import NotFound from '../../components/NotFound.vue'
import ProjectBreadcrumbItem from '../../components/breadcrumbs/ProjectBreadcrumbItem.vue'
import CountViewer from '../../components/metadata/CountViewer.vue'
import { LineChart } from 'vue-chart-3'
import { BreakingRank, getRankColor } from '../../models/difference'
import { AttributeEntry, FunctionEntry, getTypeColor } from '../../models/description'
import StatisticsSwitch from '../../components/switches/StatisticsSwitch.vue'
import LogSwitchPanel from '../../components/switches/LogSwitchPanel.vue'

const props = defineProps<{ project: string }>();

const store = useStore();
const router = useRouter();
const message = useMessage();
const loadingbar = useLoadingBar();

const showStats = ref<boolean>(false);
const showTrends = ref<boolean>(false);

const singleDurations = ref();
const pairDurations = ref();
const entryCounts = ref();
const typedEntryCounts = ref();
const rankCounts = ref();
const kindCounts = ref();
const locCounts = ref();
const bckindCounts = ref();
const bcCount = ref<number>();
const bcTypeCount = ref<number>();
const bcKwargsCount = ref<number>();
const bcClassCount = ref<number>();
const bcAliasCount = ref<number>();
const avgTotalDuration = ref<number>();
const maxTotalDuration = ref<number>();

const data = ref<PackageProductIndex>();
const error = ref<boolean>(false);

onMounted(async () => {
    loadingbar.start();
    try {
        data.value = await store.state.api.package(props.project).index();
        publicVars({ "data": data.value });
        loadingbar.finish();
    }
    catch (e) {
        console.error(e);
        error.value = true;
        loadingbar.error();
        message.error(`Failed to load data for ${props.project}.`);
    }
});

async function onTrends(value: boolean) {
    if (data.value && value && data.value && entryCounts.value == undefined && locCounts.value == undefined && typedEntryCounts.value == undefined && rankCounts.value == undefined && kindCounts.value == undefined && bckindCounts.value == undefined) {
        loadingbar.start();
        try {
            avgTotalDuration.value = 0;
            maxTotalDuration.value = 0;

            let preprocessed = await data.value.loadPreprocessed();
            publicVars({ "preprocessed": preprocessed });
            locCounts.value = getLocCounts(preprocessed);

            let extracted = await data.value.loadExtracted();
            publicVars({ "extracted": extracted });
            entryCounts.value = getEntryCounts(extracted);
            typedEntryCounts.value = getTypedEntryCounts(extracted);

            singleDurations.value = getSingleDurations(data.value.releases, preprocessed, extracted);

            let diffed = await data.value.loadDiffed();
            publicVars({ "diffed": diffed });

            rankCounts.value = getRankCounts(diffed);
            kindCounts.value = getKindCounts(diffed);
            bckindCounts.value = getBreakingKindCounts(diffed);

            let reported = await data.value.loadReported();
            publicVars({ "reported": reported });

            pairDurations.value = getPairDurations(data.value.pairs, diffed, reported);

            loadingbar.finish();
        }
        catch {
            message.error(`Failed to load trends for ${props.project}.`);
            loadingbar.error();
        }
    }
}


function getLocCounts(preprocessed: { [key: string]: Distribution }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let types = ["LOC", "Size"];
    for (let type of types) {
        rawdata[type] = [];
    }
    if (data.value) {
        for (let item of data.value.preprocessed) {
            let id = item.toString();
            labels.push(id)
            let result = preprocessed[id];
            if (result == undefined) {
                rawdata["LOC"].push(0);
                rawdata["Size"].push(0);
            }
            else {
                rawdata["LOC"].push(result.locCount);
                rawdata["Size"].push(result.fileSize);
            }
        }
    }

    let datasets = [];
    for (let type of types) {
        datasets.push({
            label: `${type} (${numberAverage(rawdata[type]).toFixed(2)})`,
            data: rawdata[type],
            borderColor: hashedColor(type),
            backgroundColor: hashedColor(type),
            tension: 0.1,
            yAxisID: type == "LOC" ? "loc" : "size",
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}


function getSingleDurations(singles: Release[], preprocessed: { [key: string]: Distribution }, extracted: { [key: string]: ApiDescription }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let types = ["Preprocess", "Extract"];
    for (let type of types) {
        rawdata[type] = [];
    }
    if (data.value) {
        for (let item of singles) {
            let id = item.toString();
            labels.push(id);
            let pre = preprocessed[id];
            if (pre == undefined) {
                rawdata["Preprocess"].push(0);
            }
            else {
                rawdata["Preprocess"].push(pre.duration);
            }
            let ext = extracted[id];
            if (ext == undefined) {
                rawdata["Extract"].push(0);
            }
            else {
                rawdata["Extract"].push(ext.duration);
            }
        }
    }

    avgTotalDuration.value = (avgTotalDuration.value ?? 0) + types.map(type => numberAverage(rawdata[type])).reduce((a, b) => a + b, 0) * 2;
    maxTotalDuration.value = (maxTotalDuration.value ?? 0) + types.map(type => Math.max(...rawdata[type])).reduce((a, b) => a + b, 0) * 2;

    let datasets = [];
    for (let type of types) {
        datasets.push({
            label: `${type} (${numberAverage(rawdata[type]).toFixed(2)})`,
            data: rawdata[type],
            borderColor: hashedColor(type),
            backgroundColor: hashedColor(type),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}

function getPairDurations(pairs: ReleasePair[], diffed: { [key: string]: ApiDifference }, reported: { [key: string]: Report }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let types = ["Diff", "Report"];
    for (let type of types) {
        rawdata[type] = [];
    }
    if (data.value) {
        for (let item of pairs) {
            let id = item.toString();
            labels.push(id);
            let diff = diffed[id];
            if (diff == undefined) {
                rawdata["Diff"].push(0);
            }
            else {
                rawdata["Diff"].push(diff.duration);
            }
            let report = reported[id];
            if (report == undefined) {
                rawdata["Report"].push(0);
            }
            else {
                rawdata["Report"].push(report.duration);
            }
        }
    }

    avgTotalDuration.value = (avgTotalDuration.value ?? 0) + types.map(type => numberAverage(rawdata[type])).reduce((a, b) => a + b, 0);
    maxTotalDuration.value = (maxTotalDuration.value ?? 0) + types.map(type => Math.max(...rawdata[type])).reduce((a, b) => a + b, 0);

    let datasets = [];
    for (let type of types) {
        datasets.push({
            label: `${type} (${numberAverage(rawdata[type]).toFixed(2)} s)`,
            data: rawdata[type],
            borderColor: hashedColor(type),
            backgroundColor: hashedColor(type),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}

function getEntryCounts(extracted: { [key: string]: ApiDescription }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let types = ["Module", "Class", "Function", "Attribute"];
    for (let type of types) {
        rawdata[type] = [];
    }
    if (data.value) {
        for (let item of data.value.extracted) {
            let id = item.toString();
            labels.push(id)
            let result = extracted[id];
            if (result == undefined) {
                rawdata["Module"].push(0);
                rawdata["Class"].push(0);
                rawdata["Function"].push(0);
                rawdata["Attribute"].push(0);
            }
            else {
                rawdata["Module"].push(Object.keys(result.modules).length);
                rawdata["Class"].push(Object.keys(result.classes).length);
                rawdata["Function"].push(Object.keys(result.functions).length);
                rawdata["Attribute"].push(Object.keys(result.attributes).length);
            }
        }
    }
    let datasets = [];
    for (let type of types) {
        datasets.push({
            label: `${type} (${numberAverage(rawdata[type]).toFixed(2)}, ${numberSum(rawdata[type])})`,
            data: rawdata[type],
            borderColor: getTypeColor(type),
            backgroundColor: getTypeColor(type),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}


function getTypedEntryCounts(extracted: { [key: string]: ApiDescription }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let types = ["Typed Function", "Typed Attribute", "Untyped Function", "Untyped Attribute"];
    let colors = ['#18a058', '#d03050', '#18a05880', '#d0305080'];
    for (let type of types) {
        rawdata[type] = [];
    }
    if (data.value) {
        for (let item of data.value.extracted) {
            let id = item.toString();
            labels.push(id)
            let result = extracted[id];
            if (result == undefined) {
                rawdata["Typed Function"].push(0);
                rawdata["Typed Attribute"].push(0);
                rawdata["Untyped Function"].push(0);
                rawdata["Untyped Attribute"].push(0);
            }
            else {
                let entries = Object.values(result.typedEntries());
                rawdata["Typed Function"].push(entries.filter(x => x instanceof FunctionEntry).length);
                rawdata["Typed Attribute"].push(entries.filter(x => x instanceof AttributeEntry).length);
                rawdata["Untyped Function"].push(Object.keys(result.functions).length - entries.filter(x => x instanceof FunctionEntry).length);
                rawdata["Untyped Attribute"].push(Object.keys(result.attributes).length - entries.filter(x => x instanceof AttributeEntry).length);
            }
        }
    }
    let datasets = [];
    for (let type of types) {
        datasets.push({
            label: `${type} (${numberAverage(rawdata[type]).toFixed(2)}, ${numberSum(rawdata[type])})`,
            data: rawdata[type],
            borderColor: colors[types.indexOf(type)],
            backgroundColor: colors[types.indexOf(type)],
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}

function getRankCounts(diffed: { [key: string]: ApiDifference }) {
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};
    let ranks = [BreakingRank.Unknown, BreakingRank.Compatible, BreakingRank.Low, BreakingRank.Medium, BreakingRank.High];
    for (let rank of ranks) {
        rawdata[BreakingRank[rank]] = [];
    }
    if (data.value) {
        for (let item of data.value.diffed) {
            let id = item.toString();
            labels.push(id);
            for (let rank of ranks) {
                let result = diffed[id];
                if (result == undefined) {
                    rawdata[BreakingRank[rank]].push(0);
                }
                else {
                    rawdata[BreakingRank[rank]].push(result.rank(rank).length);
                }
            }
        }
    }
    let datasets = [];
    for (let rank of ranks) {
        datasets.push({
            label: `${BreakingRank[rank]} (${numberAverage(rawdata[BreakingRank[rank]]).toFixed(2)}, ${numberSum(rawdata[BreakingRank[rank]])})`,
            data: rawdata[BreakingRank[rank]],
            borderColor: getRankColor(rank),
            backgroundColor: getRankColor(rank),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}

function getKindCounts(diffed: { [key: string]: ApiDifference }) {
    let kinds = new Set<string>();
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};

    if (data.value) {
        for (let item in diffed) {
            let val = diffed[item];
            for (let kind of val.kinds()) {
                kinds.add(kind);
            }
        }
        for (let kind of kinds) {
            rawdata[kind] = [];
        }
        for (let item of data.value.diffed) {
            let id = item.toString();
            labels.push(id);
            for (let kind of kinds) {
                let result = diffed[id];
                if (result == undefined) {
                    rawdata[kind].push(0);
                }
                else {
                    rawdata[kind].push(result.kind(kind).length);
                }
            }
        }
    }
    let datasets = [];
    for (let kind of kinds) {
        datasets.push({
            label: `${kind} (${numberAverage(rawdata[kind]).toFixed(2)}, ${numberSum(rawdata[kind])})`,
            data: rawdata[kind],
            borderColor: hashedColor(kind),
            backgroundColor: hashedColor(kind),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}


function getBreakingKindCounts(diffed: { [key: string]: ApiDifference }) {
    let kinds = new Set<string>();
    let labels = [];
    let rawdata: { [key: string]: number[] } = {};

    if (data.value) {
        for (let item in diffed) {
            let val = diffed[item];
            for (let kind of val.kinds()) {
                kinds.add(kind);
            }
        }
        for (let kind of kinds) {
            rawdata[kind] = [];
        }
        for (let item of data.value.diffed) {
            let id = item.toString();
            labels.push(id);
            for (let kind of kinds) {
                let result = diffed[id];
                if (result == undefined) {
                    rawdata[kind].push(0);
                }
                else {
                    let count = result.kind(kind).filter((value) => value.rank >= BreakingRank.Low).length;
                    rawdata[kind].push(count);
                }
            }
        }
    }
    let datasets = [];
    bcCount.value = 0;
    bcTypeCount.value = 0;
    bcKwargsCount.value = 0;
    bcClassCount.value = 0;
    bcAliasCount.value = 0;

    for (let kind of kinds) {
        if (numberSum(rawdata[kind]) == 0) {
            continue;
        }
        bcCount.value += numberSum(rawdata[kind]);
        if (kind.indexOf("Alias") != -1) {
            bcAliasCount.value += numberSum(rawdata[kind]);
        }
        if (kind.indexOf("BaseClass") != -1 || kind.indexOf("MethodResolutionOrder") != -1) {
            bcClassCount.value += numberSum(rawdata[kind]);
        }
        if (kind.indexOf("Type") != -1) {
            bcTypeCount.value += numberSum(rawdata[kind]);
        }
        if (kind.indexOf("Candidate") != -1) {
            bcKwargsCount.value += numberSum(rawdata[kind]);
        }
        datasets.push({
            label: `${kind} (${numberAverage(rawdata[kind]).toFixed(2)}, ${numberSum(rawdata[kind])})`,
            data: rawdata[kind],
            borderColor: hashedColor(kind),
            backgroundColor: hashedColor(kind),
            tension: 0.1,
            fill: true,
        });
    }
    return {
        labels: labels,
        datasets: datasets,
    };
}
</script>

<template>
    <n-flex vertical>
        <n-page-header :title="project ?? 'Unknown'" subtitle="Projects" @back="() => router.back()">
            <template #avatar>
                <n-avatar>
                    <n-icon :component="PackageIcon" />
                </n-avatar>
            </template>
            <template #header>
                <n-breadcrumb>
                    <HomeBreadcrumbItem />
                    <ProjectBreadcrumbItem />
                    <n-breadcrumb-item>
                        <router-link to="#">
                            <n-icon :component="PackageIcon" />
                            {{ props.project ?? "Unknown" }}
                        </router-link>
                    </n-breadcrumb-item>
                </n-breadcrumb>
            </template>
            <template #footer>
                <n-flex v-if="data">
                    <StatisticsSwitch v-model="showStats" />
                    <n-switch v-model:value="showTrends" @update-value="onTrends">
                        <template #checked>
                            <n-icon size="large" :component="TrendIcon" />
                        </template>
                        <template #unchecked>
                            <n-icon size="large" :component="TrendIcon" />
                        </template>
                    </n-switch>
                    <LogSwitchPanel :load="async () => ''" />
                </n-flex>
            </template>
        </n-page-header>

        <NotFound v-if="error" :path="router.currentRoute.value.fullPath"></NotFound>

        <n-spin v-else-if="!data" :size="80" style="width: 100%"></n-spin>

        <n-flex vertical size="large" v-if="data">
            <n-collapse-transition :show="showStats">
                <n-divider>
                    <n-flex :wrap="false" :align="'center'">
                        <n-icon size="large" :component="CountIcon" />
                        Statistics
                    </n-flex>
                </n-divider>
                <n-flex vertical>
                    <n-flex size="large">
                        <n-statistic label="Average Duration" :value="avgTotalDuration.toFixed(2)" v-if="avgTotalDuration">
                            <template #suffix>
                                <n-text>s</n-text>
                            </template>
                        </n-statistic>
                        <n-statistic label="Maximum Duration" :value="maxTotalDuration.toFixed(2)" v-if="maxTotalDuration">
                            <template #suffix>
                                <n-text>s</n-text>
                            </template>
                        </n-statistic>
                        <CountViewer :value="bcTypeCount" :total="bcCount" label="Type Breaking" v-if="bcTypeCount">
                        </CountViewer>
                        <CountViewer :value="bcKwargsCount" :total="bcCount" label="Kwargs Breaking" v-if="bcKwargsCount">
                        </CountViewer>
                        <CountViewer :value="bcClassCount" :total="bcCount" label="Base Class Breaking" v-if="bcClassCount">
                        </CountViewer>
                        <CountViewer :value="bcAliasCount" :total="bcCount" label="Alias Breaking" v-if="bcAliasCount">
                        </CountViewer>
                    </n-flex>
                </n-flex>
            </n-collapse-transition>
            <n-collapse-transition :show="showTrends">
                <n-divider>
                    <n-flex :wrap="false" :align="'center'">
                        <n-icon size="large" :component="TrendIcon" />
                        Trends
                    </n-flex>
                </n-divider>
                <n-flex vertical>
                    <LineChart :chart-data="singleDurations"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Single Processing' } }, scales: { y: { stacked: true } } }"
                        v-if="data.releases.length > 0 && singleDurations"></LineChart>
                    <LineChart :chart-data="pairDurations"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Pair Processing' } }, scales: { y: { stacked: true } } }"
                        v-if="data.pairs.length > 0 && pairDurations"></LineChart>
                    <LineChart :chart-data="locCounts" :options="{
                        plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Code Measurements' } }, scales: {
                            loc: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                            },
                            size: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                            },
                        }
                    }" v-if="data.preprocessed.length > 0 && locCounts"></LineChart>
                    <LineChart :chart-data="entryCounts"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Entries' } }, scales: { y: { stacked: true } } }"
                        v-if="data.extracted.length > 0 && entryCounts"></LineChart>
                    <LineChart :chart-data="typedEntryCounts"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Typed Entries' } }, scales: { y: { stacked: true } } }"
                        v-if="data.extracted.length > 0 && typedEntryCounts"></LineChart>
                    <LineChart :chart-data="rankCounts"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Ranks' } }, scales: { y: { stacked: true } } }"
                        v-if="data.diffed.length > 0 && rankCounts"></LineChart>
                    <LineChart :chart-data="bckindCounts"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Breaking Kinds' } }, scales: { y: { stacked: true } } }"
                        v-if="data.diffed.length > 0 && bckindCounts"></LineChart>
                    <LineChart :chart-data="kindCounts"
                        :options="{ plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Kinds' } }, scales: { y: { stacked: true } } }"
                        v-if="data.diffed.length > 0 && kindCounts"></LineChart>
                </n-flex>
            </n-collapse-transition>
            <n-divider>
                <n-flex :wrap="false" :align="'center'">
                    <n-icon size="large" :component="DataIcon" />
                    Data
                </n-flex>
            </n-divider>
            <n-collapse>
                <n-collapse-item name="releases">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="PackageIcon" />
                            Releases
                            <n-text>{{ data.releases.length }}</n-text>
                        </n-flex>
                    </template>
                    <n-space>
                        <n-button v-for="item in data.releases" :key="item.toString()" text tag="a"
                            :href="`https://pypi.org/project/${item.project}/${item.version}/`" target="_blank">{{
                                item.toString()
                            }}</n-button>
                    </n-space>
                </n-collapse-item>
                <n-collapse-item title="Preprocessed" name="preprocessed">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="PreprocessIcon" />
                            Preprocessed
                            <CountViewer :value="data.preprocessed.length" inline :total="data.releases.length" />
                        </n-flex>
                    </template>
                    <n-space>
                        <router-link :to="distributionUrl(item)" v-for="item in data.releases" :key="item.toString()" custom
                            v-slot="{ href, navigate }">
                            <n-button text tag="a" :href="href" @click="navigate"
                                :type="data.ispreprocessed(item) ? 'success' : 'error'">{{
                                    item.toString()
                                }}</n-button>
                        </router-link>
                    </n-space>
                </n-collapse-item>
                <n-collapse-item name="extracted">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="ExtractIcon" />
                            Extracted
                            <CountViewer :value="data.extracted.length" inline :total="data.preprocessed.length" />
                        </n-flex>
                    </template>
                    <n-space>
                        <router-link :to="apiUrl(item)" v-for="item in data.preprocessed" :key="item.toString()" custom
                            v-slot="{ href, navigate }">
                            <n-button text tag="a" :href="href" @click="navigate"
                                :type="data.isextracted(item) ? 'success' : 'error'">{{
                                    item.toString() }}</n-button>
                        </router-link>
                    </n-space>
                </n-collapse-item>
                <n-collapse-item name="pairs">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="VersionIcon" />
                            Pairs
                            <n-text>{{ data.pairs.length }}</n-text>
                        </n-flex>
                    </template>
                    <n-space>
                        <n-button v-for="item in data.pairs" :key="item.toString()" text tag="a">{{
                            item.toString()
                        }}</n-button>
                    </n-space>
                </n-collapse-item>
                <n-collapse-item name="diffed">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="DiffIcon" />
                            Diffed
                            <CountViewer :value="data.diffed.length" inline :total="data.pairs.length" />
                        </n-flex>
                    </template>
                    <n-space>
                        <router-link :to="changeUrl(item)" v-for="item in data.pairs" :key="item.toString()" custom
                            v-slot="{ href, navigate }">
                            <n-button text tag="a" :href="href" @click="navigate"
                                :type="data.isdiffed(item) ? 'success' : 'error'">{{
                                    item.toString() }}</n-button>
                        </router-link>
                    </n-space>
                </n-collapse-item>
                <n-collapse-item name="reported">
                    <template #header>
                        <n-flex :align="'center'">
                            <n-icon size="large" :component="ReportIcon" />
                            Reported
                            <CountViewer :value="data.reported.length" inline :total="data.diffed.length" />
                        </n-flex>
                    </template>
                    <n-space>
                        <router-link :to="reportUrl(item)" v-for="item in data.diffed" :key="item.toString()" custom
                            v-slot="{ href, navigate }">
                            <n-button text tag="a" :href="href" @click="navigate"
                                :type="data.isreported(item) ? 'success' : 'error'">{{
                                    item.toString() }}</n-button>
                        </router-link>
                    </n-space>
                </n-collapse-item>
            </n-collapse>
        </n-flex>
    </n-flex>
</template>
