#!/usr/bin/env nextflow

data_path = "'/projects/chuang-lab/jnh/flower/data'"

process get_file_list {
    conda '/projects/chuang-lab/jnh/miniconda3/envs/flower'

    output:
        file 'mov_metadata.txt' into mov_metadata

    """
    #!/usr/bin/env python
    import flowermodel.calculate_rdf as fmcal

    mov_metadata = fmcal.get_mov_metadata($data_path)
    mov_metadata = mov_metadata.iloc[:1]
    mov_metadata.to_csv('mov_metadata.txt', index=False, sep='\t')
    """
}

mov_metadata
    .collectFile()
    .splitCsv(header:true, sep:'\t')
    .map{ row -> row.movfile}
    .set {movfile}


process get_rdfs {
    conda '/projects/chuang-lab/jnh/miniconda3/envs/flower'

    input:
    val movfile

    script:
    """
    python /projects/chuang-lab/jnh/flower/notebooks/netxflow/tmp.py $movfile
    """
}

