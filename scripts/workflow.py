reference = "tair10.fasta"
annot = "tair10.gtf"

SAMPLES=["2hr_rep1", "2hr_rep2", "6hr_rep1", "6hr_rep2"]

rule all:
    input:
        'diffexpression/isoform_exp.diff',
        'assembly_result/comparison'


rule assembly:
    input:
        'mapped/{samplename}.bam'
    output:
        'assembly_result/{samplename}/transcripts.gtf',
        dir='assembly_result/{samplename}'

    shell:
        'cufflinks --num-threads 2 -o {output.dir} '
        '--frag-bias-correct {reference} {input}'


rule compose_merge:
    input:
        expand('assembly_result/{samplename}/transcripts.gtf', samplename=SAMPLES)
    output:
        txt='assembly_result/assemblies.txt'
    run:
        with open(output.txt, 'w') as output:
            print(*input, sep="\n", file=output)


rule merge_assemblies:
    input:
        'assembly_result/assemblies.txt'
    output:
        'assembly_result/merged/merged.gtf', dir='assembly_result/merged'
    shell:
        'cuffmerge -o {output.dir} -s {reference} {input}'


rule compare_assemblies:
    input:
        'assembly_result/merged/merged.gtf'
    output:
        'assembly_result/comparison/all.stats',
        dir='assembly_result/comparison'
    shell:
        'cuffcompare -o {output.dir}all -s {reference} -r {annot} {input}'


rule diff_expression:
    input:
        sample1=SAMPLES[:2],
        sample2=SAMPLES[2:],
        gtf='assembly_result/merged/merged.gtf'
    output:
        'diffexpression/gene_exp.diff', 'diffexpression/isoform_exp.diff'
    data:
        data1=",".join(sample1),
        data2=",".join(sample2)
    threads: 4
    shell:
        'cuffdiff --num-threads {threads} {gtf} {data.data1} {data.data2}'
