import React, { useState, useMemo } from 'react';
import { DataGrid, GridColDef, GridRenderCellParams, GridPaginationModel } from '@mui/x-data-grid';
import {
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Button,
  Typography,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';
import styles from './Narratives.module.scss';
import { Narrative, Filters } from '../../types';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import flag from "../../assets/icons/flag.svg";
import PlusIcon from "../../assets/icons/plus.svg";
import filterIcon from "../../assets/icons/filter.svg"
import FilterPopover from './NarrativeFilterPopover';

// Sample data: replace with your data source
const processedData: Narrative[] = [
  { id: 'NA-11051', ingestedDate: '05 Jan 2025', processedDate: '12 Jan 2025', description: 'HCP called on behalf of patient to express ...', types: ['PC','Others'], source: 'Veeva' },
  { id: 'NA-10014', ingestedDate: '02 Jan 2025', processedDate: '06 Jan 2025', description: 'Patient contacted call center for drug use ...', types: ['PC','AE'], source: 'Veeva' },
];
const pendingData: Narrative[] = [
  { id: 'NA-11052', ingestedDate: '06 Jan 2025', description: 'Pending narrative example ...', types: ['AE'], source: 'Phone' },
];

const columns: GridColDef[] = [
    {
    field: 'flag',
    headerName: '',
    width: 60,
    sortable: false,
    renderCell: () => (
      <img className={styles.flagIcon} 
        src={flag} alt="flag"
      />
    )
  },
  { field: 'id', headerName: 'Narrative ID', width: 140 },
  { field: 'ingestedDate', headerName: 'Ingested Date', width: 140 },
  { field: 'processedDate', headerName: 'Processed Date', width: 140 },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 200 },
  {
    field: 'types',
    headerName: 'Narrative type',
    width: 200,
    renderCell: (params: GridRenderCellParams<string[]>) => (
      <div className={styles.typeCell}>
        {params.value?.map((type:any) => (
          <div key={type} className={styles.typeChip}>{type}</div>
        ))}
      </div>
    )
  },
  { field: 'source', headerName: 'Source system', width: 160 }
];

const Narratives: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [search, setSearch] = useState('');
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({ page: 0, pageSize: 10 });
  const [filterAnchor, setFilterAnchor] = useState<HTMLElement | null>(null);
  const navigate = useNavigate();

  const data = tab === 0 ? processedData : pendingData;
  const filtered = useMemo(
    () => data.filter(row =>
      Object.values(row).some(val =>
        Array.isArray(val)
          ? val.join(' ').toLowerCase().includes(search.toLowerCase())
          : String(val).toLowerCase().includes(search.toLowerCase())
      )
    ),
    [data, search]
  );

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchor(event.currentTarget);
  };

  const handleFilterClose = () => setFilterAnchor(null);

  const handleFilterApply = (filters: Filters) => {
    console.log(filters);
    // TODO: apply filters to data
  };


  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <Typography variant="h5">Narratives Ingested</Typography>
        <Button
          variant="text"
          startIcon={<img className={styles.filterIcon} src={filterIcon} alt="filter"/>}
          endIcon={<ExpandMoreIcon />}
          onClick={handleFilterClick}
          className={styles.filterButton}
        >
          Filters
        </Button>
      </div>
      <FilterPopover
        anchorEl={filterAnchor}
        onClose={handleFilterClose}
        onApply={handleFilterApply}
      />
      <div className={styles.header}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          className={styles.tabsRoot}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab className={styles.text} label="Processed and classified" />
          <Tab className={styles.text} label="Pending processing" />
        </Tabs>

        <div className={styles.actions}>
          <Button
            variant="contained"
            onClick={() => navigate('/createNarrative')}
            className={styles.createButton}
          >
            <img className={styles.plusIcon} src={PlusIcon} alt="plus" />Create narrative
          </Button>
          <TextField
            className={styles.searchField}
            placeholder="Search"
            size="small"
            value={search}
            onChange={e => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              )
            }}
          />
        </div>
      </div>

      <div className={styles.gridContainer}>
        <DataGrid
          rows={filtered}
          columns={columns}
          paginationModel={paginationModel}
          onPaginationModelChange={model => setPaginationModel(model)}
          pageSizeOptions={[5, 10, 20]}
          disableRowSelectionOnClick
          sx={{ minHeight: 400 }}
        />
      </div>
    </div>
  );
};

export default Narratives;